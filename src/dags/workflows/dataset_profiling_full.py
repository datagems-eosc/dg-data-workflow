import json
from datetime import timezone, datetime
from typing import Any

from airflow.exceptions import AirflowFailException
from airflow.sdk import dag, task, get_current_context

from authorization.discovery_auth import DiscoveryAuthService
from authorization.dwo_gateway_auth import DwoGatewayAuthService
from authorization.profiler_auth import ProfilerAuthService
from common.enum import ProfileStatus
from common.extensions.callbacks import on_execute_callback, on_retry_callback, on_success_callback, \
    on_failure_callback, on_skipped_callback
from common.extensions.http_requests import http_post, http_get
from configurations import DatasetDiscoveryConfig, GatewayConfig, ProfilerConfig, DataModelManagementConfig
from documentations.dataset_profiling import DAG_DISPLAY_NAME, TRIGGER_PROFILE_ID, TRIGGER_PROFILE_DOC, \
    WAIT_FOR_COMPLETION_ID, WAIT_FOR_COMPLETION_DOC, FETCH_PROFILE_ID, FETCH_PROFILE_DOC, UPDATE_DATA_MANAGEMENT_ID, \
    UPDATE_DATA_MANAGEMENT_DOC, PROFILE_CLEANUP_ID, PROFILE_CLEANUP_DOC
from services.dataset_profiling import DAG_ID, DAG_TAGS, DAG_PARAMS, trigger_profile_builder, \
    wait_for_completion_builder, fetch_profile_builder, WAIT_FOR_COMPLETION_POKE_INTERVAL, profile_cleanup_builder, \
    update_data_model_management_builder
from services.logging.logger import Logger


@dag(DAG_ID + "FUTURE", params=DAG_PARAMS, tags=[d + "Future" for d in DAG_TAGS],
     dag_display_name=DAG_DISPLAY_NAME + " Future")
def dataset_profiling():
    profiler_auth_service = ProfilerAuthService()
    gateway_auth_service = DwoGatewayAuthService()
    discovery_auth_service = DiscoveryAuthService()
    profiler_config = ProfilerConfig()
    gateway_config = GatewayConfig()
    discovery_config = DatasetDiscoveryConfig()
    dmm_config = DataModelManagementConfig()

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=TRIGGER_PROFILE_ID, doc_md=TRIGGER_PROFILE_DOC)
    def trigger_profile(is_light: bool) -> Any:
        log = Logger()
        trigger_profile_url, trigger_profile_headers, trigger_profile_payload = trigger_profile_builder(
            profiler_auth_service.get_token(), get_current_context(), profiler_config, is_light)
        trigger_response = http_post(url=trigger_profile_url, data=trigger_profile_payload,
                                     headers=trigger_profile_headers)
        log.info(f"Server responded with {trigger_response}")
        return trigger_response["job_id"]

    @task.sensor(poke_interval=WAIT_FOR_COMPLETION_POKE_INTERVAL, mode="reschedule",
                 on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
                 on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
                 on_skipped_callback=on_skipped_callback, task_id=WAIT_FOR_COMPLETION_ID,
                 doc_md=WAIT_FOR_COMPLETION_DOC)
    def wait_for_completion(profile_id: str) -> Any:
        log = Logger()
        url, headers = wait_for_completion_builder(gateway_auth_service.get_token(), get_current_context(),
                                                   profiler_config, profile_id)
        status_response = http_get(url=url, headers=headers)
        profile_status = ProfileStatus(status_response)
        if profile_status is ProfileStatus.CLEANED_UP:
            error_message = f"Profile {profile_id} is cleaned up"
            log.error(error_message)
            raise AirflowFailException(error_message)
        else:
            log.info(f"Profile {profile_id} status is {profile_status}")
        return profile_status is ProfileStatus.HEAVY_PROFILES_READY or profile_status is ProfileStatus.LIGHT_PROFILE_READY

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=FETCH_PROFILE_ID, doc_md=FETCH_PROFILE_DOC)
    def fetch_profile(profile_id: str) -> str:
        log = Logger()
        url, headers = fetch_profile_builder(gateway_auth_service.get_token(), get_current_context(), profiler_config,
                                             profile_id)
        fetch_profile_response = http_get(url=url, headers=headers)
        log.info(f"Server responded with {fetch_profile_response}")
        return json.dumps(fetch_profile_response)

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=UPDATE_DATA_MANAGEMENT_ID, doc_md=UPDATE_DATA_MANAGEMENT_DOC)
    def update_data_management(stringified_profile_data: str) -> Any:
        log = Logger()
        url, headers, payload = update_data_model_management_builder(gateway_auth_service.get_token(),
                                                                     get_current_context(), dmm_config,
                                                                     stringified_profile_data,
                                                                     datetime.now(timezone.utc))
        log.info(payload)
        response = http_post(url=url, headers=headers, data=payload)
        log.info(f"Server responded with {response}")
        return response

    # @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
    #       on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
    #       on_skipped_callback=on_skipped_callback, task_id=PASS_INDEX_FILES_ID, doc_md=PASS_INDEX_FILES_DOC)
    # def pass_index_files(stringified_profile_data: str) -> Any:
    #     log = Logger()
    #     url, headers, payload = pass_index_files_builder(discovery_auth_service.get_token(), get_current_context(),
    #                                                      discovery_config,
    #                                                      stringified_profile_data)
    #     response = http_post(url=url, headers=headers, data=payload)
    #     log.info(f"Server responded with {response}")
    #     return response

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=PROFILE_CLEANUP_ID, doc_md=PROFILE_CLEANUP_DOC)
    def profile_cleanup(profile_id: str) -> Any:
        log = Logger()
        url, headers, payload = profile_cleanup_builder(profiler_auth_service.get_token(), get_current_context(),
                                                        profiler_config, profile_id)
        response = http_post(url=url, headers=headers, data=payload)
        log.info(f"Server responded with {response}")
        return response

    light_fetched_id = trigger_profile(True)
    heavy_fetched_id = trigger_profile(False)

    light_completed_procedure = wait_for_completion(light_fetched_id)
    heavy_completed_procedure = wait_for_completion(heavy_fetched_id)

    fetched_light_profile = fetch_profile(light_fetched_id)
    fetched_heavy_profile = fetch_profile(heavy_fetched_id)

    data_management_heavy_id = update_data_management(fetched_heavy_profile)
    data_management_light_id = update_data_management(fetched_light_profile)

    # passed_index_files_response = pass_index_files(fetched_heavy_profile)

    heavy_profile_cleanup_response = profile_cleanup(heavy_fetched_id)

    light_completed_procedure >> fetched_light_profile
    data_management_light_id >> data_management_heavy_id >> heavy_profile_cleanup_response
    heavy_completed_procedure >> fetched_heavy_profile >> heavy_profile_cleanup_response


dataset_profiling()
