import json
from datetime import timezone, datetime, date
from typing import Any

from airflow.exceptions import AirflowFailException
from airflow.sdk import dag, task, Param

from authorization.moma_management_auth import MomaManagementAuthService
from authorization.profiler_auth import ProfilerAuthService
from common.enum import ProfileStatus, MomaProfileType, DataStoreKind
from common.extensions.callbacks import on_execute_callback, on_retry_callback, on_success_callback, \
    on_skipped_callback, on_failure_callback, on_success_profiling_callback
from common.extensions.http_requests import http_post, http_get, http_put
from common.extensions.xcom_logging import xcom_task_logging
from configurations import ProfilerConfig, DataModelManagementConfig, \
    MomaManagementConfig, DbServerRegistryConfig
from documentations.dataset_profiling import DAG_DISPLAY_NAME, TRIGGER_PROFILE_ID, TRIGGER_PROFILE_DOC, \
    WAIT_FOR_COMPLETION_ID, WAIT_FOR_COMPLETION_DOC, FETCH_PROFILE_ID, FETCH_PROFILE_DOC, UPDATE_DATA_MANAGEMENT_ID, \
    UPDATE_DATA_MANAGEMENT_DOC, PROFILE_CLEANUP_ID, PROFILE_CLEANUP_DOC, CONVERT_PROFILING_ID, CONVERT_PROFILING_DOC
from services.dataset_profiling import DAG_ID, trigger_profile_builder, \
    wait_for_completion_builder, fetch_profile_builder, WAIT_FOR_COMPLETION_POKE_INTERVAL, profile_cleanup_builder, \
    update_data_model_management_builder, convert_profiling_builder

DAG_PARAMS = {
    "id": Param("00000000-0000-0000-0000-000000000000", type=["string"], format="uuid"),
    "name": Param(None, type=["null", "string"]),
    "description": Param(None, type=["null", "string"]),
    "license": Param(None, type=["null", "string"]),
    "url": Param(None, type=["null", "string"], format="uri"),
    "headline": Param(None, type=["null", "string"]),
    "keywords": Param(None, type=["null", "array"]),
    "fields_of_science": Param(None, type=["null", "array"]),
    "languages": Param(None, type=["null", "array"]),
    "countries": Param(None, type=["null", "array"]),
    "date_published": Param(f"{date.today()}", type=["null", "string"], format="date"),
    "dataset_file_path": Param(None, type=["null", "string"]),
    "userId": Param(None, type=["null", "string"]),
    "citeAs": Param(None, type=["null", "string"]),
    "conformsTo": Param(None, type=["null", "string"]),
    "data_store_kind": Param(DataStoreKind.FileSystem.value, type="integer", enum=[c.value for c in DataStoreKind]),
    "archivedAt": Param(None, type=["null", "string"]),
    "doi": Param(None, type=["null", "string"]),
    "database_name": Param(None, type=["null", "string"]),
    "workflow_process_step_information": Param(type="object"),
}


@dag(DAG_ID + "_test", params=DAG_PARAMS, tags=["DatasetProfiling_test", ], dag_display_name=DAG_DISPLAY_NAME + "_test")
def dataset_profiling():
    profiler_auth_service = ProfilerAuthService()
    profiler_config = ProfilerConfig()
    db_server_registry = DbServerRegistryConfig()
    dmm_config = DataModelManagementConfig()
    moma_config = MomaManagementConfig()
    moma_auth = MomaManagementAuthService()

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=TRIGGER_PROFILE_ID, doc_md=TRIGGER_PROFILE_DOC)
    def trigger_profile(is_light: bool) -> Any:
        with xcom_task_logging() as log:
            dag_context = log.context
            trigger_profile_url, trigger_profile_headers, trigger_profile_payload = trigger_profile_builder(
                profiler_auth_service.get_token(), dag_context, profiler_config, db_server_registry, is_light)
            log.info_payload("payload", trigger_profile_payload, True)
            trigger_response = http_post(url=trigger_profile_url, data=trigger_profile_payload,
                                         headers=trigger_profile_headers)
            log.info_payload("Server response", trigger_response, True)
            return trigger_response["job_id"]

    @task.sensor(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
                 on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
                 on_skipped_callback=on_skipped_callback, poke_interval=WAIT_FOR_COMPLETION_POKE_INTERVAL,
                 mode="reschedule",
                 task_id=WAIT_FOR_COMPLETION_ID,
                 doc_md=WAIT_FOR_COMPLETION_DOC)
    def wait_for_completion(profile_id: str) -> Any:
        with xcom_task_logging() as log:
            dag_context = log.context
            url, headers = wait_for_completion_builder(profiler_auth_service.get_token(), dag_context,
                                                       profiler_config, profile_id)
            status_response = http_get(url=url, headers=headers)
            profile_status = ProfileStatus(status_response["status"])
            if profile_status is ProfileStatus.CLEANED_UP:
                error_message = f"Profile {profile_id} is cleaned up"
                log.error(error_message)
                raise AirflowFailException(error_message)
            elif profile_status is ProfileStatus.FAILED:
                error_message = f"Profile {profile_id} has failed"
                log.error(error_message)
                raise AirflowFailException(error_message)
            else:
                log.info_payload(f"Profile {profile_id} status", profile_status)
            return profile_status is ProfileStatus.HEAVY_PROFILE_READY

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=FETCH_PROFILE_ID, doc_md=FETCH_PROFILE_DOC)
    def fetch_profile(profile_id: str) -> str:
        with xcom_task_logging() as log:
            dag_context = log.context
            url, headers = fetch_profile_builder(profiler_auth_service.get_token(), dag_context, profiler_config,
                                                 profile_id)
            fetch_profile_response = http_get(url=url, headers=headers)
            log.info_payload("server response", fetch_profile_response, True)
            return json.dumps(fetch_profile_response)

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=CONVERT_PROFILING_ID, doc_md=CONVERT_PROFILING_DOC)
    def convert_profiling(stringified_profile_data: str, profile_type: str) -> Any:
        with xcom_task_logging() as log:
            dag_context = log.context
            url, headers, payload = convert_profiling_builder(moma_auth.get_token(), dag_context,
                                                              moma_config, stringified_profile_data, profile_type)
            log.info_payload("payload", payload, True)
            response = http_post(url=url, headers=headers, data=payload)
            log.info_payload("server response", response, True)
            return json.dumps(response)

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=UPDATE_DATA_MANAGEMENT_ID, doc_md=UPDATE_DATA_MANAGEMENT_DOC)
    def update_data_management(converted_profile: str, original_profile: str, profile_type: str) -> Any:
        with xcom_task_logging() as log:
            dag_context = log.context
            url, headers, payload = update_data_model_management_builder(moma_auth.get_token(),
                                                                         dag_context, dmm_config,
                                                                         converted_profile, original_profile,
                                                                         datetime.now(timezone.utc), profile_type)
            log.info_payload("payload", payload, True)
            response = http_put(url=url, headers=headers, data=payload)
            log.info_payload("server response", response, True)
            return response

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_profiling_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=PROFILE_CLEANUP_ID, doc_md=PROFILE_CLEANUP_DOC)
    def profile_cleanup(profile_id: str) -> Any:
        with xcom_task_logging() as log:
            dag_context = log.context
            url, headers, payload = profile_cleanup_builder(profiler_auth_service.get_token(), dag_context,
                                                            profiler_config, profile_id)
            log.info_payload("payload", payload, True)
            response = http_post(url=url, headers=headers, data=payload)
            log.info_payload("server response", response, True)
            return response

    heavy_fetched_id = trigger_profile(False)

    heavy_completed_procedure = wait_for_completion(heavy_fetched_id)

    fetched_heavy_profile = fetch_profile(heavy_fetched_id)

    converted_heavy = convert_profiling(fetched_heavy_profile, MomaProfileType.HEAVY.value)

    data_management_heavy_id = update_data_management(converted_heavy, fetched_heavy_profile,
                                                      MomaProfileType.HEAVY.value)

    heavy_profile_cleanup_response = profile_cleanup(heavy_fetched_id)

    heavy_completed_procedure >> fetched_heavy_profile
    data_management_heavy_id >> heavy_profile_cleanup_response


dataset_profiling()
