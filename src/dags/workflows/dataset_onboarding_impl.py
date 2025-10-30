import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from airflow.exceptions import AirflowException
from airflow.sdk import dag, task, get_current_context

from config.dwo_gateway_config import GatewayConfig
from config.workflows_dataset_onboarding_config import DatasetOnboardingConfig
from services.data_retriever import DataRetriever
from services.data_staging import DataStagingService
from services.dwo_gateway_auth import DwoGatewayAuthService
from services.logger import Logger
from utils.http_requests import http_post
from workflows.dataset_onboarding_config import DAG_ID, DAG_TAGS, DAG_PARAMS, config_onboarding, process_location


@dag(DAG_ID, params=DAG_PARAMS, tags=DAG_TAGS)
def dataset_onboarding():
    @task()
    def stage_dataset_files():
        dag_context = get_current_context()
        log = Logger()
        config = DatasetOnboardingConfig()
        log.info("Stage Dataset File Task")
        stream_service = DataRetriever()
        stage_service = DataStagingService()

        results = []
        failed_locations = []

        with ThreadPoolExecutor() as executor:
            future_to_location = {
                executor.submit(process_location, loc, stream_service, stage_service, log, config): loc
                for loc in json.loads(dag_context["params"]["dataLocations"])
            }

            for future in as_completed(future_to_location):
                loc = future_to_location[future]
                try:
                    result = future.result()
                    if result:
                        results.append(result)
                    else:
                        failed_locations.append(loc)
                except Exception as e:
                    log.error(f"Unexpected error processing {loc.get('url')}: {e}")
                    failed_locations.append(loc)

        if failed_locations:
            raise AirflowException(
                f"Failed to process dataset locations: "
                f"{[l.get('url') for l in failed_locations]}"
            )
        return results

    @task()
    def request_onboarding():
        dag_context = get_current_context()
        log = Logger()
        gateway_config = GatewayConfig()
        log.info("Request onboarding")
        access_token = DwoGatewayAuthService().get_token()
        gateway_url, headers, payload = config_onboarding(access_token, dag_context, gateway_config)

        return http_post(url=gateway_url, data=payload,
                         headers=headers)

    stage_dataset_files = stage_dataset_files()
    request_onboarding = request_onboarding()

    stage_dataset_files >> request_onboarding


dataset_onboarding()
