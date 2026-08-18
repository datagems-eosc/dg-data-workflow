import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, timedelta, date
from typing import Any

import requests.exceptions
from airflow.exceptions import AirflowException, AirflowFailException
from airflow.sdk import dag, task, Param

from authorization.data_model_management_auth import DataModelManagementAuthService
from common.enum import DataLocationKind
from common.extensions.callbacks import on_execute_callback, on_success_callback, on_skipped_callback, \
    on_retry_callback, on_failure_callback, on_success_onboarding_callback
from common.extensions.file_extensions import process_location, get_staged_path, create_folder, create_file
from common.extensions.http_requests import http_post, http_put
from common.extensions.xcom_logging import xcom_task_logging
from common.types import DataLocation
from configurations import DataModelManagementConfig, DatasetOnboardingConfig
from documentations.dataset_onboarding_full import DAG_DISPLAY_NAME, STAGE_DATASET_FILES_ID, STAGE_DATASET_FILES_DOC, \
    REGISTER_DATASET_ID, REGISTER_DATASET_DOC, LOAD_DATASET_ID, LOAD_DATASET_DOC
from services.data_management import DataRetriever, DataStagingService
from services.dataset_onboarding import DAG_ID, register_dataset_builder, load_dataset_builder

DAG_PARAMS = {
    "id": Param("00000000-0000-0000-0000-000000000000", type="string", format="uuid"),
    "name": Param(None, type=["null", "string"]),
    "description": Param(None, type=["null", "string"]),
    "headline": Param(None, type=["null", "string"]),
    "fields_of_science": Param(None, type=["null", "array"]),
    "languages": Param(None, type=["null", "array"]),
    "keywords": Param(None, type=["null", "array"]),
    "countries": Param(None, type=["null", "array"]),
    "publishedUrl": Param(None, type=["null", "string"], format="uri"),
    "citeAs": Param(None, type=["null", "string"]),
    "license": Param(None, type=["null", "string"]),
    "dataLocations": Param([], type="string"),
    "date_published": Param(f"{date.today()}", type=["null", "string"], format="date"),
    "userId": Param(None, type=["null", "string"]),
    "doi": Param(None, type=["null", "string"]),
    "workflow_process_step_information": Param(type="object")
}


@dag(DAG_ID + "_test", params=DAG_PARAMS, tags=["DatasetOnboarding_test", ],
     dag_display_name=DAG_DISPLAY_NAME + "_test")
def dataset_onboarding():
    dataset_onboarding_config = DatasetOnboardingConfig()
    dmm_config = DataModelManagementConfig()
    dmm_auth = DataModelManagementAuthService()

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=STAGE_DATASET_FILES_ID, doc_md=STAGE_DATASET_FILES_DOC)
    def stage_dataset_files() -> list[dict[str, int | str | None]]:
        with xcom_task_logging() as log:
            dag_context = log.context
            stream_service = DataRetriever()
            stage_service = DataStagingService()

            results: list[DataLocation] = []
            failed_locations = []
            data_locations = [DataLocation.from_dict(d) for d in json.loads(dag_context["params"]["dataLocations"])]
            with ThreadPoolExecutor() as executor:
                future_to_location = {
                    executor.submit(process_location, dag_context["params"]["id"], loc, stream_service, stage_service,
                                    log,
                                    dataset_onboarding_config): loc for loc in data_locations}

                for future in as_completed(future_to_location):
                    loc = future_to_location[future]
                    try:
                        result = future.result()
                        if result:
                            results.append(result)
                        else:
                            failed_locations.append(loc)
                    except Exception as e:
                        log.error(f"Unexpected error processing {loc.location}: {e}")
                        failed_locations.append(loc)

            if failed_locations:
                raise AirflowException(f"Failed to process dataset locations: "
                                       f"{[l.location for l in failed_locations]}")
            return [res.to_dict() for res in results]

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=REGISTER_DATASET_ID, doc_md=REGISTER_DATASET_DOC)
    def register_dataset(raw_data_locations: list[dict[str, int | str | None]]) -> Any:
        with xcom_task_logging() as log:
            dag_context = log.context
            url, headers, payload = register_dataset_builder(dmm_auth.get_token(), dag_context, dmm_config,
                                                             [DataLocation.from_dict(d) for d in raw_data_locations],
                                                             datetime.now(timezone.utc))
            log.info_payload("payload", payload, True)
            response = http_post(url=url, headers=headers, data=payload)
            log.info_payload("server response", response, True)
            return response

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_onboarding_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=LOAD_DATASET_ID, doc_md=LOAD_DATASET_DOC, retries=5,
          retry_delay=timedelta(seconds=2))
    def load_dataset(raw_data_locations: list[dict[str, int | str | None]]) -> Any:
        with xcom_task_logging() as log:
            dag_context = log.context
            dataset_id = dag_context["params"]["id"]
            data_locations = [DataLocation.from_dict(d) for d in raw_data_locations]
            is_database_load = (
                    len(data_locations) == 1
                    and data_locations[0].kind == DataLocationKind.Database
            )

            if is_database_load:
                new_dir = create_folder(get_staged_path(dataset_id))
                _ = create_file(new_dir.as_posix(), dataset_id)

            url, headers, payload = load_dataset_builder(dmm_auth.get_token(), dag_context, dmm_config, data_locations,
                                                         datetime.now(timezone.utc))
            log.info_payload("payload", payload, True)
            try:
                response = http_put(url=url, headers=headers, data=payload)
            except requests.exceptions.HTTPError as ex:
                status_code = ex.response.status_code if ex.response is not None else None
                error_message = ""
                if ex.response is not None:
                    try:
                        response_body = ex.response.json()
                        error_message = str(response_body.get("error", ""))
                    except ValueError:
                        error_message = ex.response.text or ""

                if is_database_load and status_code == 404 and "Source dataset not found at expected location" in error_message:
                    raise AirflowException(
                        f"Source dataset is not visible yet at expected location. Retrying...") from ex

                raise AirflowFailException(
                    f"Load dataset failed with a non-retryable HTTP error. "
                    f"Status code: {status_code}. "
                    f"Error: {error_message or ex}"
                ) from ex
            except Exception as ex:
                raise AirflowFailException(
                    f"Load dataset failed with a non-retryable error. "
                    f"Original error: {ex}"
                ) from ex

            log.info_payload("server response", response, True)
            return response

    staged_files_response = stage_dataset_files()
    register_response = register_dataset(staged_files_response)
    load_response = load_dataset(staged_files_response)

    register_response >> load_response


dataset_onboarding()
