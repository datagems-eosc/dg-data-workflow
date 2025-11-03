from airflow.sdk import dag, task, get_current_context

from common.extensions.http_requests import http_post
from authorization.dwo_gateway_auth import DwoGatewayAuthService
from authorization import ProfilerAuthService
from services.logging.logger import Logger
from workflows.dataset_profiling_config import DAG_ID, DAG_TAGS, DAG_PARAMS, config_profiling


@dag(DAG_ID, params=DAG_PARAMS, tags=DAG_TAGS)
def dataset_profiling():
    @task()
    def create_profile():
        dag_context = get_current_context()
        log = Logger()
        log.info("Request to create profile")
        access_token = ProfilerAuthService().get_token()
        trigger_profile_url, trigger_profile_headers, trigger_profile_payload = config_profiling(access_token,
                                                                                                 dag_context)

    @task()
    def request_profiling():
        dag_context = get_current_context()
        log = Logger()
        log.info("Request profiling")
        access_token = DwoGatewayAuthService().get_token()
        gateway_url, headers, payload = config_profiling(access_token, dag_context)
        profiling_response = http_post(url=gateway_url, data=payload,
                                       headers=headers)
        log.info(profiling_response)
        return profiling_response

    @task()
    def request_data_management(profiled_id: str):
        dag_context = get_current_context()
        log = Logger()
        log.info("Request data management")
        return "TODO"

    _ = request_data_management(request_profiling())


dataset_profiling()
