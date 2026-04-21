from airflow.sdk import Context

from configurations import DatasetPackagingConfig


def dataset_packaging_builder(auth_token: str, dag_context: Context, config: DatasetPackagingConfig) -> tuple[
    str, dict[str, str]]:
    url: str = config.options.base_url + config.options.profiler.get_profile.format(id=dag_context["params"]["id"])
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}", "Connection": "keep-alive"}
    return url, headers