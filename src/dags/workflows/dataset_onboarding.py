import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from airflow.exceptions import AirflowException
from airflow.sdk import dag, task, get_current_context

from authorization.dwo_gateway_auth import DwoGatewayAuthService
from common.extensions.callbacks import on_execute_callback, on_success_callback, on_skipped_callback, \
    on_retry_callback, on_failure_callback
from common.extensions.file_extensions import process_location
from common.extensions.http_requests import http_post
from common.types import DataLocation
from documentations.dataset_onboarding import DAG_DESCRIPTION, STAGE_DATASET_FILES_DOC, \
    STAGE_DATASET_FILES_ID, REQUEST_ONBOARDING_ID, REQUEST_ONBOARDING_DOC, DAG_DISPLAY_NAME
from configurations import GatewayConfig, DatasetOnboardingConfig
from services.data_management.data_retriever import DataRetriever
from services.data_management.data_staging import DataStagingService
from services.dataset_onboarding import DAG_ID, DAG_PARAMS, DAG_TAGS, \
    request_onboarding_builder
from services.logging.logger import Logger


@dag(DAG_ID, params=DAG_PARAMS, tags=DAG_TAGS, dag_display_name=DAG_DISPLAY_NAME, description=DAG_DESCRIPTION)
def dataset_onboarding():
    dataset_onboarding_config = DatasetOnboardingConfig()
    gateway_config = GatewayConfig()
    gateway_auth_service = DwoGatewayAuthService()

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=STAGE_DATASET_FILES_ID, doc_md=STAGE_DATASET_FILES_DOC)
    def stage_dataset_files() -> list[dict[str, int | str | None]]:
        dag_context = get_current_context()
        log = Logger()
        stream_service = DataRetriever()
        stage_service = DataStagingService()

        results: list[DataLocation] = []
        failed_locations = []
        data_locations = [DataLocation.from_dict(d) for d in json.loads(dag_context["params"]["dataLocations"])]
        with ThreadPoolExecutor() as executor:
            future_to_location = {
                executor.submit(process_location, dag_context["params"]["id"], loc, stream_service, stage_service, log,
                                dataset_onboarding_config): loc
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
                    log.error(f"Unexpected error processing {loc.get('location')}: {e}")
                    failed_locations.append(loc)

        if failed_locations:
            raise AirflowException(
                f"Failed to process dataset locations: "
                f"{[l.get('location') for l in failed_locations]}"
            )
        return [res.to_dict() for res in results]

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=REQUEST_ONBOARDING_ID, doc_md=REQUEST_ONBOARDING_DOC)
    def request_onboarding(raw_data_locations: list[dict[str, int | str | None]]) -> Any:
        data_locations = [DataLocation.from_dict(d) for d in raw_data_locations]
        dag_context = get_current_context()
        log = Logger()
        access_token = gateway_auth_service.get_token()
        gateway_url, headers, payload = request_onboarding_builder(access_token, dag_context, gateway_config,
                                                                   data_locations)
        log.info(f"Payload:\n{payload}\n")
        response = http_post(url=gateway_url, data=payload,
                             headers=headers)
        log.info(f"Server responded with\n{response}\n")
        return response

    stage_dataset_files_response = stage_dataset_files()
    _ = request_onboarding(stage_dataset_files_response)


dataset_onboarding()
