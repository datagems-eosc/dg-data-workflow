from airflow.sdk import dag, task, get_current_context

from authorization.dataset_recommender_auth import DatasetRecommenderAuthService
from common.extensions.callbacks import on_execute_callback, on_retry_callback, on_success_callback, \
    on_failure_callback, on_skipped_callback
from common.extensions.http_requests import http_post
from configurations import DatasetRecommenderConfig
from documentations.dataset_recommender_registering import DAG_DISPLAY_NAME, IMPORT_DATASET_ID, IMPORT_DATASET_DOC
from services.dataset_recommender import DAG_ID, DAG_PARAMS, DAG_TAGS, dataset_recommendation_registering_builder
from services.logging import Logger


@dag(DAG_ID, params=DAG_PARAMS, tags=DAG_TAGS, dag_display_name=DAG_DISPLAY_NAME)
def dataset_recommendation_registering():
    dataset_packaging_config = DatasetRecommenderConfig()
    dataset_packaging_auth = DatasetRecommenderAuthService()

    @task(on_execute_callback=on_execute_callback, on_retry_callback=on_retry_callback,
          on_success_callback=on_success_callback, on_failure_callback=on_failure_callback,
          on_skipped_callback=on_skipped_callback, task_id=IMPORT_DATASET_ID, doc_md=IMPORT_DATASET_DOC)
    def import_dataset() -> bool:
        log = Logger()
        context = get_current_context()

        url, headers = dataset_recommendation_registering_builder(dataset_packaging_auth.get_token(), context,
                                                                  dataset_packaging_config)
        log.info_payload("headers", headers, True)
        response = http_post(url=url, headers=headers)
        log.info_payload("Server response", response, True)
        return True

    _ = import_dataset()


dataset_recommendation_registering()
