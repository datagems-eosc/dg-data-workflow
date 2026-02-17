import json
from datetime import timedelta, datetime

import psycopg2
from airflow.sdk import task, dag, get_current_context, BaseHook, Connection

from common.extensions.callbacks import on_execute_callback, on_retry_callback, on_success_callback, \
    on_failure_callback, on_skipped_callback
from common.extensions.http_requests import http_get
from common.types import FeatureCollection
from configurations import NoaGeoConfig
from documentations.geo_ingest import DAG_DISPLAY_NAME, DESCRIPTION
from services.geo_ingest import DAG_PARAMS, DAG_TAGS, DAG_ID, fetch_weather_builder, upsert_feature_collection, \
    MINUTES_TIMEDELTA
from services.logging import Logger
from services.meteo_db_context import PostgresDatabase


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
    def store_data(stringified_data: str) -> None:
        dag_context = get_current_context()
        log = Logger()
        db_context = PostgresDatabase()
        obj = FeatureCollection.model_validate(json.loads(stringified_data))
        upsert_feature_collection(db_context, obj, log)
        return

    fetched_data = fetch_weather()
    store_data(fetched_data)


geo_ingest()
