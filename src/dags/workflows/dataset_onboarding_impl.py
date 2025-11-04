import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from airflow.exceptions import AirflowException
from airflow.sdk import dag, task, get_current_context

from authorization.dwo_gateway_auth import DwoGatewayAuthService
from common.extensions.http_requests import http_post
from common.types.data_location import DataLocation
from configurations.dwo_gateway_config import GatewayConfig
from configurations.workflows_dataset_onboarding_config import DatasetOnboardingConfig
from services.data_management.data_retriever import DataRetriever
from services.data_management.data_staging import DataStagingService
from services.logging.logger import Logger
from workflows.dataset_onboarding_config import DAG_ID, DAG_TAGS, DAG_PARAMS, request_onboarding_builder, process_location


@dag(DAG_ID, params=DAG_PARAMS, tags=DAG_TAGS)
def dataset_onboarding():
    @task()
    def stage_dataset_files() -> list[dict[str, int | str | None]]:
        dag_context = get_current_context()
        log = Logger()
        config = DatasetOnboardingConfig()
        log.info("Stage Dataset File Task")
        stream_service = DataRetriever()
        stage_service = DataStagingService()

        results: list[DataLocation] = []
        failed_locations = []
        data_locations = [DataLocation.from_dict(d) for d in json.loads(dag_context["params"]["dataLocations"])]
        with ThreadPoolExecutor() as executor:
            future_to_location = {
                executor.submit(process_location, dag_context["params"]["id"], loc, stream_service, stage_service, log,
                                config): loc
                for loc in data_locations
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
        return [res.to_dict() for res in results]

    @task()
    def request_onboarding(raw_data_locations: list[dict[str, int | str | None]]) -> Any:
        data_locations = [DataLocation.from_dict(d) for d in raw_data_locations]
        dag_context = get_current_context()
        log = Logger()
        gateway_config = GatewayConfig()
        log.info("Request onboarding")
        access_token = DwoGatewayAuthService().get_token()
        gateway_url, headers, payload = request_onboarding_builder(access_token, dag_context, gateway_config, data_locations)

        return http_post(url=gateway_url, data=payload,
                         headers=headers)

    _ = request_onboarding(stage_dataset_files())


dataset_onboarding()
