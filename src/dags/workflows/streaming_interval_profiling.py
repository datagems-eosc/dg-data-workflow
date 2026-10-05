import json
from datetime import timedelta, datetime

from airflow.sdk import task, dag, get_current_context

from common.extensions.http_requests import http_post
from configurations import StreamingIntervalProfilerConfig
from authorization.streaming_interval_profiler_auth import StreamingIntervalProfilerAuthService
from documentations.geo_ingest import DAG_DISPLAY_NAME, DESCRIPTION
from services.streaming_interval_profiling import DAG_PARAMS, DAG_TAGS, DAG_ID, fetch_profile_builder, \
    MINUTES_TIMEDELTA
from services.logging import Logger


@dag(DAG_ID, tags=DAG_TAGS, dag_display_name=DAG_DISPLAY_NAME, description=DESCRIPTION, params=DAG_PARAMS,
     schedule=timedelta(minutes=MINUTES_TIMEDELTA), start_date=datetime(year=2000, month=1, day=1))
def streaming_interval_profiling():
    streaming_interval_profiler_config = StreamingIntervalProfilerConfig()
    streaming_interval_profiler_auth = StreamingIntervalProfilerAuthService()

    @task()
    def fetch_profile() -> str:
        dag_context = get_current_context()
        log = Logger()
        url, headers, body = fetch_profile_builder(streaming_interval_profiler_config, dag_context, streaming_interval_profiler_auth.get_token())
        response = http_post(url=url, headers=headers, data=body)
        if isinstance(response, str):
            response = json.loads(response)
        log.info(f"Server responded with {response}")
        return json.dumps(response)

    @task()
    def store_data(stringified_data: str) -> None:
        
        return

    fetched_data = fetch_profile()
    store_data(fetched_data)


streaming_interval_profiling()
