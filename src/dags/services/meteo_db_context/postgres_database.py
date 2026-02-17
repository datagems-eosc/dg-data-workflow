from typing import Dict, List, Tuple

import psycopg2
from airflow.sdk import Connection, BaseHook

from common.types import DatabaseInterface
from services.logging import Logger


class PostgresDatabase(DatabaseInterface):
    """PostgreSQL / TimescaleDB implementation."""

    def __init__(self):
        self.conn = None
        self.logger = Logger()
        self._connect()

    def _connect(self):
        try:
            connection_string = BaseHook.get_connection("timescale_db")
            self.conn = psycopg2.connect(
                host=connection_string.host,
                port=connection_string.port,
                dbname=connection_string.schema,
                user=connection_string.login,
                password=connection_string.password,
            )
            self.conn.autocommit = True
            self.logger.info("Connected to PostgreSQL/TimescaleDB")
        except psycopg2.Error as e:
            self.logger.error(f"PostgreSQL Connection Error: {e}")
            raise

    def insert_station(self, station_id: str, info: Dict) -> bool:
        try:
            with self.conn.cursor() as cur:
                cur.execute("""
                            INSERT INTO stations (station_id, station_name_en, station_name_gr,
                                                  latitude, longitude, elevation, first_seen, last_seen)
                            VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP) 
                            ON CONFLICT(station_id) DO
                            UPDATE SET
                                station_name_en = EXCLUDED.station_name_en,
                                latitude = EXCLUDED.latitude,
                                longitude = EXCLUDED.longitude,
                                last_seen = CURRENT_TIMESTAMP
                            """, (
                                station_id, info.get('station_name_en'), info.get('station_name_gr'),
                                info.get('latitude'), info.get('longitude'), info.get('elevation')
                            ))
            return True
        except psycopg2.Error as e:
            self.logger.error(f"PG Station Insert Error: {e}")
            return False

    def insert_observations_batch(self, observations: List[Tuple]) -> int:
        count = 0
        try:
            with self.conn.cursor() as cur:
                for obs in observations:
                    cur.execute("""
                                INSERT INTO observations (time, station_id, temp_out, hi_temp, low_temp, out_hum,
                                                          bar, rain, wind_speed, wind_dir, wind_dir_str,
                                                          hi_speed, hi_dir, hi_dir_str)
                                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                        %s) ON CONFLICT DO NOTHING
                                """, obs)
                    count += cur.rowcount
            return count
        except psycopg2.Error as e2:
            self.logger.error(f"PG Batch Error: {e2}")
            return 0

    def log_collection(self, status: str, stations_count: int, obs_count: int, message: str = ""):
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO collection_log (status, stations_count, observations_count, message) VALUES (%s, %s, %s, %s)",
                    (status, stations_count, obs_count, message))
        except:
            pass

    def get_stats(self) -> Dict:
        return {"type": "PostgreSQL/TimescaleDB"}

    def close(self):
        if self.conn: self.conn.close()

    def __del__(self):
        self.close()