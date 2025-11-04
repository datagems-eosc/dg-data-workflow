from airflow.sdk import dag, task, get_current_context

from authorization.dwo_gateway_auth import DwoGatewayAuthService
from authorization.profiler_auth import ProfilerAuthService
from common.enum.profile_status import ProfileStatus
from common.extensions.http_requests import http_post, http_get
from configurations.dataset_profiler_config import ProfilerConfig
from services.logging.logger import Logger
from workflows.dataset_profiling_config import DAG_ID, DAG_TAGS, DAG_PARAMS, trigger_profile_builder, \
    ask_profile_status, fetch_ready_profile


@dag(DAG_ID, params=DAG_PARAMS, tags=DAG_TAGS)
def dataset_profiling():
    @task()
    def trigger_profile():
        dag_context = get_current_context()
        log = Logger()
        log.info("Request to create profile")
        config = ProfilerConfig()
        access_token = ProfilerAuthService().get_token()
        trigger_profile_url, trigger_profile_headers, trigger_profile_payload = trigger_profile_builder(access_token,
                                                                                                        dag_context,
                                                                                                        config)
        trigger_response = http_post(url=trigger_profile_url, data=trigger_profile_payload,
                                     headers=trigger_profile_headers)
        return trigger_response["job_id"]

    @task.sensor(poke_interval=15, timeout=3600, mode="reschedule")
    def wait_for_completion(profile_id: str):
        dag_context = get_current_context()
        log = Logger()
        log.info("Ask for profile status")
        config = ProfilerConfig()
        access_token = DwoGatewayAuthService().get_token()
        url, headers = ask_profile_status(access_token, dag_context, config, profile_id)
        status_response = http_get(url=url, headers=headers)
        profile_status = ProfileStatus(status_response)
        log.info(status_response)
        # TODO: ask for info for handling of additional enum values, since some may denote failed processing
        return profile_status is ProfileStatus.HeavyProfileReady or profile_status is ProfileStatus.LightProfileReady

    @task()
    def fetch_profile(profile_id: str):
        dag_context = get_current_context()
        log = Logger()
        log.info("Fetch ready profile")
        config = ProfilerConfig()
        access_token = DwoGatewayAuthService().get_token()
        url, headers = fetch_ready_profile(access_token, dag_context, config, profile_id)
        fetch_profile_response = http_get(url=url, headers=headers)
        log.info(fetch_profile_response)
        return 1

    fetched_id = trigger_profile()
    completed_procedure = wait_for_completion(fetched_id)
    fetched_profile = fetch_profile(fetched_id)

    fetched_id >> completed_procedure >> fetched_profile

dataset_profiling()
