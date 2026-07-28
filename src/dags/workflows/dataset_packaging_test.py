from airflow.sdk import dag, task, Param

from authorization.dataset_packaging_auth import DatasetPackagingAuthService
from common.extensions.callbacks import on_execute_callback, on_skipped_callback, \
    on_retry_callback, on_failure_callback, on_success_packaging_callback
from common.extensions.http_requests import http_post
from common.extensions.xcom_logging import xcom_task_logging
from configurations import DatasetPackagingConfig
from documentations.dataset_packaging import DAG_DISPLAY_NAME, IMPORT_DATASET_ID, IMPORT_DATASET_DOC
from services.dataset_packaging import DAG_ID, dataset_packaging_builder

DAG_PARAMS = {
    "id": Param("00000000-0000-0000-0000-000000000000", type=["string"], format="uuid"),
    "workflow_process_step_information": Param(type="object"),
}


@dag(DAG_ID + '_test', params=DAG_PARAMS, tags=["DatasetPackaging_test", ], dag_display_name=DAG_DISPLAY_NAME + '_test')
def dataset_packaging():
    dataset_packaging_config = DatasetPackagingConfig()
    dataset_packaging_auth = DatasetPackagingAuthService()

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_packaging_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=IMPORT_DATASET_ID, doc_md=IMPORT_DATASET_DOC)
    def import_dataset() -> bool:
        with xcom_task_logging() as log:
            context = log.context
            url, headers = dataset_packaging_builder(dataset_packaging_auth.get_token(), context,
                                                     dataset_packaging_config)
            response = http_post(url=url, headers=headers)
            log.info_payload("Server response", response, True)
            return True

    _ = import_dataset()


dataset_packaging()
