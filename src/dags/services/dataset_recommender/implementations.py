from airflow.sdk import Context

from configurations import DatasetRecommenderConfig


def dataset_recommendation_registering_builder(auth_token: str, dag_context: Context,
                                               config: DatasetRecommenderConfig) -> tuple[str, dict[str, str]]:
    url: str = config.options.base_url + config.options.endpoints.add.format(id=dag_context["params"]["id"])
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}", "Connection": "keep-alive"}
    return url, headers
