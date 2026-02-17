from datetime import datetime

from airflow.sdk import Context

from common.types import FeatureCollection
from configurations import NoaGeoConfig
from services.logging import Logger
from services.meteo_db_context import PostgresDatabase


def fetch_weather_builder(config: NoaGeoConfig, dag_context: Context) -> tuple[str, dict[str, str]]:
    noa_url: str = config.options.base_url + config.options.endpoints.geojson
    headers = {"Content-Type": "application/json", "Connection": "keep-alive"}
    return noa_url, headers


def upsert_feature_collection(db_context: PostgresDatabase, feature_collection: FeatureCollection, logger: Logger) -> \
tuple[bool, str]:
    try:
        features = feature_collection.features
        if not features: return False, "No data"
        station_info_list = []
        observations_list = []

        for feature in features:
            props = feature.properties
            coords = feature.geometry.coordinates
            station_id = props.station_file if props.station_file else props.fid
            if not station_id: continue
            station_info_list.append({'station_id': station_id, 'station_name_en': props.station_name_en,
                'station_name_gr': props.station_name_gr, 'latitude': coords[1], 'longitude': coords[0],
                'elevation': coords[2] if len(coords) > 2 else None})

            ts = props.ts if props.ts else 0
            if ts > 0:
                time_dt = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
                observations_list.append(
                    (time_dt, station_id, props.temp_out, props.hi_temp, props.low_temp, props.out_hum, props.bar,
                     props.rain, props.wind_speed, props.wind_dir, props.wind_dir_str, props.hi_speed, props.hi_dir,
                     props.hi_dir_str))

        for info in station_info_list: db_context.insert_station(info['station_id'], info)
        count = db_context.insert_observations_batch(observations_list)

        msg = f"Stored {count} obs from {len(station_info_list)} stations"
        logger.info(msg)
        db_context.log_collection('SUCCESS', len(station_info_list), count, msg)
        return True, msg
    except Exception as e:
        msg = f"Error: {e}"
        logger.error(msg)
        db_context.log_collection('ERROR', 0, 0, msg)
        return False, msg
