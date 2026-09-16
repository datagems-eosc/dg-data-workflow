from typing import Any

from airflow.exceptions import AirflowFailException
from airflow.sdk import dag, task

from authorization.dataset_linking_auth import DatasetLinkingAuthService
from common.enum import DatasetLinkingStatus
from common.extensions.callbacks import on_execute_callback, on_retry_callback, on_success_callback, \
    on_skipped_callback, on_failure_callback, on_success_profiling_callback
from common.extensions.http_requests import http_post, http_get, http_put
from common.extensions.xcom_logging import xcom_task_logging
from configurations import DatasetLinkingConfig
from documentations.dataset_linking_report import DAG_DISPLAY_NAME, START_REPORT_JOB_ID, START_REPORT_JOB_DOC, \
    WAIT_FOR_COMPLETION_ID, WAIT_FOR_COMPLETION_DOC
from services.dataset_linking_report import DAG_ID, DAG_PARAMS, DAG_TAGS, trigger_report_builder, \
    WAIT_FOR_COMPLETION_POKE_INTERVAL, wait_for_completion_builder


@dag(DAG_ID, params=DAG_PARAMS, tags=DAG_TAGS, dag_display_name=DAG_DISPLAY_NAME)
def dataset_linking_report():
    dataset_linking_auth_service = DatasetLinkingAuthService()
    dataset_linking_config = DatasetLinkingConfig()

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=START_REPORT_JOB_ID, doc_md=START_REPORT_JOB_DOC)
    def trigger_report() -> Any:
        with xcom_task_logging() as log:
            dag_context = log.context
            trigger_report_url, trigger_report_headers, trigger_report_payload = trigger_report_builder(
                dataset_linking_auth_service.get_token(), dag_context, dataset_linking_config)
            log.info_payload("payload", trigger_report_payload, True)
            trigger_response = http_post(url=trigger_report_url, data=trigger_report_payload,
                                         headers=trigger_report_headers)
            log.info_payload("Server response", trigger_response, True)
            return trigger_response["job_id"]

    @task.sensor(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
                 on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
                 on_skipped_callback=on_skipped_callback, poke_interval=WAIT_FOR_COMPLETION_POKE_INTERVAL,
                 mode="reschedule",
                 task_id=WAIT_FOR_COMPLETION_ID,
                 doc_md=WAIT_FOR_COMPLETION_DOC)
    def wait_for_completion(job_id: str) -> Any:
        with xcom_task_logging() as log:
            dag_context = log.context
            url, headers = wait_for_completion_builder(dataset_linking_auth_service.get_token(), dag_context,
                                                       dataset_linking_config, job_id)
            status_response = http_get(url=url, headers=headers)
            linking_status = DatasetLinkingStatus(status_response["status"])
            if linking_status is DatasetLinkingStatus.FAILED:
                error_message = f"Profile {job_id} has failed"
                log.error(error_message)
                raise AirflowFailException(error_message)
            else:
                log.info_payload(f"Profile {job_id} status", linking_status)
            return linking_status is DatasetLinkingStatus.COMPLETED



    fetched_id = trigger_report()
    _ = wait_for_completion(fetched_id)


dataset_linking_report()
