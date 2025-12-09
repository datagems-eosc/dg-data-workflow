import json
from typing import Any

from airflow.exceptions import AirflowFailException
from airflow.sdk import dag, task, get_current_context

from authorization.dwo_gateway_auth import DwoGatewayAuthService
from authorization.profiler_auth import ProfilerAuthService
from common.enum.profile_status import ProfileStatus
from common.extensions.callbacks import on_execute_callback, on_retry_callback, on_success_callback, \
    on_failure_callback, on_skipped_callback
from common.extensions.http_requests import http_post, http_get
from configurations.dwo_gateway_config import GatewayConfig
from configurations.workflows_dataset_profiler_config import ProfilerConfig
from documentations.dataset_profiling import DAG_DISPLAY_NAME, TRIGGER_PROFILE_ID, TRIGGER_PROFILE_DOC, \
    WAIT_FOR_COMPLETION_ID, WAIT_FOR_COMPLETION_DOC, FETCH_PROFILE_ID, FETCH_PROFILE_DOC, UPDATE_DATA_MANAGEMENT_ID, \
    UPDATE_DATA_MANAGEMENT_DOC
from services.dataset_profiling import DAG_ID, DAG_TAGS, DAG_PARAMS, trigger_profile_builder, \
    wait_for_completion_builder, fetch_profile_builder, update_data_management_builder, \
    WAIT_FOR_COMPLETION_POKE_INTERVAL
from services.logging.logger import Logger


@dag(DAG_ID, params=DAG_PARAMS, tags=DAG_TAGS, dag_display_name=DAG_DISPLAY_NAME)
def dataset_profiling():
    profiler_auth_service = ProfilerAuthService()
    gateway_auth_service = DwoGatewayAuthService()
    profiler_config = ProfilerConfig()
    gateway_config = GatewayConfig()

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=TRIGGER_PROFILE_ID, doc_md=TRIGGER_PROFILE_DOC)
    def trigger_profile(is_light: bool) -> Any:
        dag_context = get_current_context()
        log = Logger()
        config = profiler_config
        access_token = profiler_auth_service.get_token()
        trigger_profile_url, trigger_profile_headers, trigger_profile_payload = trigger_profile_builder(access_token,
                                                                                                        dag_context,
                                                                                                        config,
                                                                                                        is_light)
        log.info(f"Payload:\n{trigger_profile_payload}\n")
        trigger_response = http_post(url=trigger_profile_url, data=trigger_profile_payload,
                                     headers=trigger_profile_headers)
        log.info(f"Server responded with\n{trigger_response}\n")
        return trigger_response["job_id"]

    @task.sensor(poke_interval=WAIT_FOR_COMPLETION_POKE_INTERVAL, mode="reschedule",
                 on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
                 on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
                 on_skipped_callback=on_skipped_callback, task_id=WAIT_FOR_COMPLETION_ID,
                 doc_md=WAIT_FOR_COMPLETION_DOC)
    def wait_for_completion(profile_id: str) -> Any:
        dag_context = get_current_context()
        log = Logger()
        config = profiler_config
        access_token = gateway_auth_service.get_token()
        url, headers = wait_for_completion_builder(access_token, dag_context, config, profile_id)
        status_response = http_get(url=url, headers=headers)
        profile_status = ProfileStatus(status_response)
        if profile_status is ProfileStatus.CLEANED_UP:
            error_message = f"Profile {profile_id} is cleaned up"
            log.error(error_message)
            raise AirflowFailException(error_message)
        elif profile_status is ProfileStatus.FAILED:
            error_message = f"Profile {profile_id} has failed"
            log.error(error_message)
            raise AirflowFailException(error_message)
        else:
            log.info(f"Profile {profile_id} status is {profile_status}\n")
        return profile_status is ProfileStatus.HEAVY_PROFILES_READY or profile_status is ProfileStatus.LIGHT_PROFILE_READY

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=FETCH_PROFILE_ID, doc_md=FETCH_PROFILE_DOC)
    def fetch_profile(profile_id: str) -> str:
        dag_context = get_current_context()
        log = Logger()
        config = profiler_config
        access_token = gateway_auth_service.get_token()
        url, headers = fetch_profile_builder(access_token, dag_context, config, profile_id)
        fetch_profile_response = http_get(url=url, headers=headers)
        log.info(f"Server responded with\n{fetch_profile_response}\n")
        return json.dumps(fetch_profile_response)

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=UPDATE_DATA_MANAGEMENT_ID, doc_md=UPDATE_DATA_MANAGEMENT_DOC)
    def update_data_management(stringified_profile_data: str) -> Any:
        dag_context = get_current_context()
        log = Logger()
        access_token = gateway_auth_service.get_token()
        url, headers, payload = update_data_management_builder(access_token, dag_context, gateway_config,
                                                               stringified_profile_data)
        log.info(f"Payload:\n{payload}\n")
        response = http_post(url=url, headers=headers, data=payload)
        log.info(f"Server responded with\n{response}\n")
        return response

    light_fetched_id = trigger_profile(True)
    heavy_fetched_id = trigger_profile(False)

    light_completed_procedure = wait_for_completion(light_fetched_id)
    heavy_completed_procedure = wait_for_completion(heavy_fetched_id)

    fetched_light_profile = fetch_profile(light_fetched_id)
    fetched_heavy_profile = fetch_profile(heavy_fetched_id)

    data_management_heavy_id = update_data_management(fetched_heavy_profile)
    data_management_light_id = update_data_management(fetched_light_profile)

    light_completed_procedure >> fetched_light_profile
    heavy_completed_procedure >> fetched_heavy_profile
    data_management_light_id >> data_management_heavy_id


dataset_profiling()
