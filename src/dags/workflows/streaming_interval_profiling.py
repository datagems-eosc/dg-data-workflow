import json
from datetime import timedelta, datetime

from airflow.sdk import task, dag

from authorization.data_model_management_auth import DataModelManagementAuthService
from authorization.streaming_interval_profiler_auth import StreamingIntervalProfilerAuthService
from common.extensions.http_requests import http_get, http_post, http_put
from common.extensions.xcom_logging import xcom_task_logging
from configurations import StreamingIntervalProfilerConfig, DataModelManagementConfig
from documentations.streaming_interval_profiling import DAG_DISPLAY_NAME, DESCRIPTION
from services.streaming_interval_profiling import DAG_PARAMS, DAG_TAGS, DAG_ID, fetch_profile_builder, \
    MINUTES_TIMEDELTA, upsert_moma_builder, fetch_moma_builder


@dag(DAG_ID, tags=DAG_TAGS, dag_display_name=DAG_DISPLAY_NAME, description=DESCRIPTION, params=DAG_PARAMS,
     schedule=timedelta(minutes=MINUTES_TIMEDELTA), start_date=datetime(year=2000, month=1, day=1))
def streaming_interval_profiling():
    streaming_interval_profiler_config = StreamingIntervalProfilerConfig()
    streaming_interval_profiler_auth = StreamingIntervalProfilerAuthService()
    dmm_config = DataModelManagementConfig()
    dmm_auth = DataModelManagementAuthService()

    @task()
    def fetch_profile() -> str:
        with xcom_task_logging() as log:
            dag_context = log.context
            url, headers, body = fetch_profile_builder(streaming_interval_profiler_config, dag_context,
                                                       streaming_interval_profiler_auth.get_token())
            log.info_payload("payload", body, True)
            response = http_post(url=url, headers=headers, data=body)
            if isinstance(response, str):
                response = json.loads(response)
            log.info_payload("server response", response, True)
            return json.dumps(response)

    @task()
    def store_data(stringified_data: str) -> None:
        with xcom_task_logging() as log:
            dag_context = log.context
            url, headers = fetch_moma_builder(dmm_config, dmm_auth.get_token(), stringified_data)
            response = http_get(url=url, headers=headers)
            log.info_payload("payload", body, True)
            url, headers, body = upsert_moma_builder(dmm_config, dmm_auth.get_token(), stringified_data, response)
            log.info_payload("payload", body, True)
            response = http_put(url=url, headers=headers, data=body)
            log.info_payload("server response", response, True)
            return

    fetched_data = fetch_profile()
    store_data(fetched_data)


streaming_interval_profiling()
