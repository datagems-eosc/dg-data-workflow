import json
from datetime import timedelta, datetime

import psycopg2
from airflow.sdk import task, dag, get_current_context, BaseHook

from common.extensions.callbacks import on_execute_callback, on_retry_callback, on_success_callback, \
    on_failure_callback, on_skipped_callback
from common.extensions.http_requests import http_get
from common.types import FeatureCollection
from configurations import NoaGeoConfig
from documentations.geo_ingest import DAG_DISPLAY_NAME, DESCRIPTION
from services.geo_ingest import DAG_PARAMS, DAG_TAGS, DAG_ID, fetch_weather_builder, upsert_feature_collection, \
    MINUTES_TIMEDELTA
from services.logging import Logger


@dag(DAG_ID, tags=DAG_TAGS, dag_display_name=DAG_DISPLAY_NAME, description=DESCRIPTION, params=DAG_PARAMS,
     schedule=timedelta(minutes=MINUTES_TIMEDELTA), start_date=datetime(year=2000, month=1, day=1))
def geo_ingest():
    noa_geo_config = NoaGeoConfig()

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback)
    def fetch_weather() -> str:
        dag_context = get_current_context()
        log = Logger()
        url, headers = fetch_weather_builder(noa_geo_config, dag_context)
        response = http_get(url=url, headers=headers)
        log.info(f"Server responded with {response}")
        return json.dumps(response)

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback)
    def process_data(stringified_data: str) -> str:
        dag_context = get_current_context()
        log = Logger()
        obj = FeatureCollection.model_validate(json.loads(stringified_data))
        stringified_obj = obj.model_dump_json()
        log.info(f"This is the transformed data: {stringified_obj}")
        return stringified_obj

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback)
    def store_data(stringified_data: str) -> None:
        dag_context = get_current_context()
        log = Logger()
        obj = FeatureCollection.model_validate(json.loads(stringified_data))
        try:
            conn = BaseHook.get_connection("timescale_db")
            with psycopg2.connect(host=conn.host, port=conn.port, dbname=conn.schema, user=conn.login,
                                  password=conn.password, ) as pg:
                upsert_feature_collection(pg, obj)
            return
        except Exception as e:
            log.error(f"{e}")
            raise

    fetched_data = fetch_weather()
    processed_data = process_data(fetched_data)
    store_data(processed_data)


geo_ingest()
