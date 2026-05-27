from urllib.parse import urlencode

from airflow.sdk import Context

from configurations import ProfilerConfig, DatasetDiscoveryConfig


def fetch_profile_path_builder(auth_token: str, dag_context: Context, config: ProfilerConfig) -> tuple[
    str, dict[str, str]]:
    url: str = config.options.base_url + config.options.profiler.fetch_cdd_profile.format(
        id=dag_context["params"]["id"])
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}", "Connection": "keep-alive"}
    return url, headers


def begin_ingestion_builder(auth_token: str, path: str, config: DatasetDiscoveryConfig) -> tuple[str, dict[str, str]]:
    params = {"path_to_profile": path}
    url: str = config.options.base_url + config.options.endpoints.insert + urlencode(params)
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}", "Connection": "keep-alive"}
    return url, headers


def wait_for_completion_builder(auth_token: str, job_id: str, config: DatasetDiscoveryConfig) -> tuple[
    str, dict[str, str]]:
    url: str = config.options.base_url + config.options.endpoints.status.format(id=job_id)
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}", "Connection": "keep-alive"}
    return url, headers
