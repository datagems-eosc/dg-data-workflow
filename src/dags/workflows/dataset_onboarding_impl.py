import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from airflow.sdk import dag, task, get_current_context

from config.dwo_gateway_config import GatewayConfig
from config.workflows_dataset_onboarding_config import DatasetOnboardingConfig
from services.data_retriever import DataRetriever
from services.data_staging import DataStagingService
from services.dwo_gateway_auth import DwoGatewayAuthService
from services.logger import Logger
from utils.http_requests import http_post
from workflows.dataset_onboarding_config import DAG_ID, DAG_TAGS, DAG_PARAMS, config_onboarding


@dag(DAG_ID, params=DAG_PARAMS, tags=DAG_TAGS)
def dataset_onboarding():
    def process_location(location, stream_service: DataRetriever, stage_service: DataStagingService, log: Logger,
                         config: DatasetOnboardingConfig):
        kind: str = location["kind"]
        url = location["url"]
        local_path = f"{config.local_staging_path}{kind}_{abs(hash(url))}.dat"
        try:
            with stream_service.retrieve(kind, url) as stream:
                if kind.lower() != "remote":
                    stage_service.store(stream, local_path)
            return local_path
        except Exception as e:
            log.error(e)

    @task()
    def stage_dataset_files():
        dag_context = get_current_context()
        log = Logger()
        config = DatasetOnboardingConfig()
        log.info("Stage Dataset File Task")
        stream_service = DataRetriever()
        stage_service = DataStagingService()

        results = []
        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_location, loc, stream_service, stage_service, log, config) for loc in
                       json.loads(dag_context["params"]["dataLocations"])]
            for future in as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)
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
