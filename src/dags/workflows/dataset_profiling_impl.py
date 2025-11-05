import json

from airflow.exceptions import AirflowFailException
from airflow.sdk import dag, task, get_current_context

from authorization.dwo_gateway_auth import DwoGatewayAuthService
from authorization.profiler_auth import ProfilerAuthService
from common.enum.profile_status import ProfileStatus
from common.extensions.http_requests import http_post, http_get
from configurations.dwo_gateway_config import GatewayConfig
from configurations.workflows_dataset_profiler_config import ProfilerConfig
from services.logging.logger import Logger
from workflows.dataset_profiling_config import DAG_ID, DAG_TAGS, DAG_PARAMS, trigger_profile_builder, \
    wait_for_completion_builder, fetch_profile_builder, update_data_management_builder, \
    WAIT_FOR_COMPLETION_POKE_INTERVAL


@dag(DAG_ID, params=DAG_PARAMS, tags=DAG_TAGS)
def dataset_profiling():
    profiler_auth_service = ProfilerAuthService()
    gateway_auth_service = DwoGatewayAuthService()
    profiler_config = ProfilerConfig()
    gateway_config = GatewayConfig()

    @task()
    def trigger_profile():
        dag_context = get_current_context()
        log = Logger()
        log.info("Request to create profile")
        config = profiler_config
        access_token = profiler_auth_service.get_token()
        trigger_profile_url, trigger_profile_headers, trigger_profile_payload = trigger_profile_builder(access_token,
                                                                                                        dag_context,
                                                                                                        config)
        trigger_response = http_post(url=trigger_profile_url, data=trigger_profile_payload,
                                     headers=trigger_profile_headers)
        log.info(f"Server responded with {trigger_response}")
        return trigger_response["job_id"]

    @task.sensor(poke_interval=WAIT_FOR_COMPLETION_POKE_INTERVAL, mode="reschedule")
    def wait_for_completion(profile_id: str):
        dag_context = get_current_context()
        log = Logger()
        log.info("Ask for profile status")
        config = profiler_config
        access_token = gateway_auth_service.get_token()
        url, headers = wait_for_completion_builder(access_token, dag_context, config, profile_id)
        status_response = http_get(url=url, headers=headers)
        profile_status = ProfileStatus(status_response)
        if profile_status is ProfileStatus.CLEANED_UP:
            error_message = f"Profile {profile_id} is cleaned up"
            log.error(error_message)
            raise AirflowFailException(error_message)
        else:
            log.info(f"Profile {profile_id} status is {profile_status}")
        return profile_status is ProfileStatus.HEAVY_PROFILES_READY or profile_status is ProfileStatus.LIGHT_PROFILE_READY

    @task()
    def fetch_profile(profile_id: str):
        dag_context = get_current_context()
        log = Logger()
        log.info("Fetch ready profile")
        config = profiler_config
        access_token = gateway_auth_service.get_token()
        url, headers = fetch_profile_builder(access_token, dag_context, config, profile_id)
        fetch_profile_response = http_get(url=url, headers=headers)
        log.info(f"Server responded with {fetch_profile_response}")
        return json.dumps(fetch_profile_response)

    @task()
    def update_data_management(stringified_profile_data: str):
        dag_context = get_current_context()
        log = Logger()
        log.info("Fetch ready profile")
        access_token = gateway_auth_service.get_token()
        url, headers, payload = update_data_management_builder(access_token, dag_context, gateway_config,
                                                               stringified_profile_data)
        response = http_post(url=url, headers=headers, data=payload)
        log.info(f"Server responded with {response}")
        return response

    fetched_id = trigger_profile()
    completed_procedure = wait_for_completion(fetched_id)
    fetched_profile = fetch_profile(fetched_id)
    data_management_id = update_data_management(fetched_profile)

    fetched_id >> completed_procedure >> fetched_profile >> data_management_id


dataset_profiling()
