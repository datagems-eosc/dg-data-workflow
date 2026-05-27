from typing import Any

from airflow.exceptions import AirflowFailException
from airflow.sdk import dag, task, get_current_context

from authorization.discovery_auth import DiscoveryAuthService
from authorization.profiler_auth import ProfilerAuthService
from common.enum import CddIngestionStatus
from common.extensions.callbacks import on_execute_callback, on_success_callback, on_skipped_callback, \
    on_retry_callback, on_failure_callback
from common.extensions.http_requests import http_get, http_post
from configurations import DatasetDiscoveryConfig, ProfilerConfig
from documentations.cdd_ingest import DAG_DISPLAY_NAME, CDD_FETCH_FILE_ID, CDD_FETCH_FILE_DOC, CDD_BEGIN_INGEST_ID, \
    CDD_BEGIN_INGEST_DOC, WAIT_FOR_COMPLETION_ID, WAIT_FOR_COMPLETION_DOC
from services.cdd_ingestion import DAG_ID, DAG_PARAMS, DAG_TAGS, fetch_profile_path_builder, begin_ingestion_builder, \
    WAIT_FOR_COMPLETION_POKE_INTERVAL, wait_for_completion_builder
from services.logging import Logger


@dag(DAG_ID, params=DAG_PARAMS, tags=DAG_TAGS, dag_display_name=DAG_DISPLAY_NAME)
def discovery_ingestion():
    discovery_config = DatasetDiscoveryConfig()
    discovery_auth = DiscoveryAuthService()
    profiler_config = ProfilerConfig()
    profiler_auth = ProfilerAuthService()

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=CDD_FETCH_FILE_ID, doc_md=CDD_FETCH_FILE_DOC)
    def fetch_profile_path():
        log = Logger()
        context = get_current_context()

        url, headers = fetch_profile_path_builder(profiler_auth.get_token(), context, profiler_config)
        log.info_payload("request url", url)

        response = http_get(url=url, headers=headers)
        log.info_payload("server response", response, True)

        path: str | None = response["cdd_profile_path"]
        if path is None:
            error_message = f"Dataset is not profiled."
            log.error(error_message)
            raise AirflowFailException(error_message)
        return path

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=CDD_BEGIN_INGEST_ID, doc_md=CDD_BEGIN_INGEST_DOC)
    def begin_ingestion(path: str):
        log = Logger()
        context = get_current_context()

        url, headers = begin_ingestion_builder(discovery_auth.get_token(), path, discovery_config)
        log.info_payload("request url", url)

        response = http_post(url=url, headers=headers)
        log.info_payload("server response", response, True)

        job_id: str = response["job_id"]
        return job_id

    @task.sensor(poke_interval=WAIT_FOR_COMPLETION_POKE_INTERVAL, mode="reschedule",
                 on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
                 on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
                 on_skipped_callback=on_skipped_callback, task_id=WAIT_FOR_COMPLETION_ID,
                 doc_md=WAIT_FOR_COMPLETION_DOC)
    def wait_for_completion(job_id: str) -> Any:
        log = Logger()

        url, headers = wait_for_completion_builder(discovery_auth.get_token(), job_id, discovery_config)
        log.info_payload("request url", url)

        response = http_get(url=url, headers=headers)
        log.info_payload("server response", response, True)

        status = CddIngestionStatus(response["status"])
        if status is CddIngestionStatus.FAILED:
            error_message = f"Cdd ingestion {job_id} has failed"
            log.error(error_message)
            raise AirflowFailException(error_message)
        return status is CddIngestionStatus.COMPLETED

    _ = wait_for_completion(begin_ingestion(fetch_profile_path()))

discovery_ingestion()