import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from typing import Any

from airflow.exceptions import AirflowException
from airflow.sdk import dag, task, get_current_context

from authorization.data_model_management_auth import DataModelManagementAuthService
from common.extensions.callbacks import on_execute_callback, on_success_callback, on_skipped_callback, \
    on_retry_callback, on_failure_callback
from common.extensions.file_extensions import process_location
from common.extensions.http_requests import http_post, http_put
from common.types import DataLocation
from configurations import DataModelManagementConfig, DatasetOnboardingConfig
from documentations.dataset_onboarding_full import DAG_DISPLAY_NAME, STAGE_DATASET_FILES_ID, \
    STAGE_DATASET_FILES_DOC, REGISTER_DATASET_ID, REGISTER_DATASET_DOC, LOAD_DATASET_ID, LOAD_DATASET_DOC
from services.data_management.data_retriever import DataRetriever
from services.data_management.data_staging import DataStagingService
from services.dataset_onboarding import DAG_ID, DAG_TAGS, DAG_PARAMS, \
    register_dataset_builder, load_dataset_builder
from services.logging.logger import Logger


@dag(DAG_ID + "_FUTURE", params=DAG_PARAMS, tags=[d + "Future" for d in DAG_TAGS],
     dag_display_name=DAG_DISPLAY_NAME)
def dataset_onboarding():
    dataset_onboarding_config = DatasetOnboardingConfig()
    dmm_config = DataModelManagementConfig()
    dmm_auth = DataModelManagementAuthService()

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
          on_skipped_callback=on_skipped_callback, task_id=REGISTER_DATASET_ID, doc_md=REGISTER_DATASET_DOC)
    def register_dataset(raw_data_locations: list[dict[str, int | str | None]]) -> Any:
        log = Logger()
        url, headers, payload = register_dataset_builder(dmm_auth.get_token(), get_current_context(), dmm_config,
                                                         [DataLocation.from_dict(d) for d in raw_data_locations],
                                                         datetime.now(timezone.utc))
        response = http_post(url=url, headers=headers, data=payload)
        log.info(response)
        return response

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=LOAD_DATASET_ID, doc_md=LOAD_DATASET_DOC)
    def load_dataset(raw_data_locations: list[dict[str, int | str | None]]) -> Any:
        log = Logger()
        url, headers, payload = load_dataset_builder(dmm_auth.get_token(), get_current_context(), dmm_config,
                                                     [DataLocation.from_dict(d) for d in raw_data_locations],
                                                     datetime.now(timezone.utc))
        log.info(payload)
        response = http_put(url=url, headers=headers, data=payload)
        log.info(response)
        return response

    staged_files_response = stage_dataset_files()
    register_response = register_dataset(staged_files_response)
    load_response = load_dataset(staged_files_response)

    register_response >> load_response


dataset_onboarding()
