from datetime import datetime, timezone
from typing import Optional
from zoneinfo import ZoneInfo

import psycopg2
from airflow.sdk import Context
from psycopg2.extras import execute_values

from configurations import NoaGeoConfig
from services.geo_ingest.constants import STATION_UPSERT_SQL, OBS_UPSERT_SQL


def fetch_weather_builder(config: NoaGeoConfig, dag_context: Context) -> tuple[str, dict[str, str]]:
    noa_url: str = config.options.base_url + config.options.endpoints.geojson
    headers = {"Content-Type": "application/json", "Connection": "keep-alive"}
    return noa_url, headers


def utc_time_from_source(ts: Optional[int], date: Optional[datetime], ) -> datetime:
    if ts is not None:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc)
    if date is None:
        raise ValueError("Both properties.ts and properties.date are missing")
    if date.tzinfo is None:
        date = date.replace(tzinfo=ZoneInfo("Europe/Athens"))
    return date.astimezone(timezone.utc)


def upsert_feature_collection(conn, feature_collection) -> None:
    stations_by_id: dict[int, dict] = {}
    observations: list[dict] = []
    for feat in feature_collection.features:
        p = feat.properties
        g = feat.geometry
        station_id = int(p.fid)
        lon = float(g.coordinates[0])
        lat = float(g.coordinates[1])
        elev = float(g.coordinates[2]) if len(g.coordinates) > 2 and g.coordinates[2] is not None else None
        stations_by_id.setdefault(station_id, {"station_id": station_id, "station_file": p.station_file,
                                               "station_name_gr": p.station_name_gr,
                                               "station_name_en": p.station_name_en, "longitude": lon, "latitude": lat,
                                               "elevation_m": elev, })
        obs_time = utc_time_from_source(p.ts, p.date)
        observations.append(
            {"time": obs_time, "station_id": station_id, "temp_out_c": p.temp_out, "hi_temp_c": p.hi_temp,
             "low_temp_c": p.low_temp, "out_hum_pct": int(p.out_hum) if p.out_hum is not None else None,
             "bar_hpa": p.bar, "rain_mm": p.rain, "wind_speed_ms": p.wind_speed, "wind_dir_deg": p.wind_dir,
             "wind_dir_str": p.wind_dir_str, "hi_speed_ms": p.hi_speed,
             "hi_dir_deg": float(p.hi_dir) if p.hi_dir is not None else None, "hi_dir_str": p.hi_dir_str,
             "source_ts": p.ts, "source_date_text": p.date.isoformat() if p.date else None, })

    station_rows = list(stations_by_id.values())
    try:
        with conn.cursor() as cur:
            for row in station_rows:
                cur.execute(STATION_UPSERT_SQL, row)
            psycopg2.extras.execute_batch(cur, OBS_UPSERT_SQL, observations)
        conn.commit()
    except Exception:
        conn.rollback()
        raise
