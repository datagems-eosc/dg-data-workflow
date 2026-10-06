from typing import Any

from airflow.sdk import Context

from configurations import StreamingIntervalProfilerConfig


def fetch_profile_builder(config: StreamingIntervalProfilerConfig, dag_context: Context, auth_token: str) -> tuple[
    str, dict[str, str], dict[str, Any | None]]:
    url: str = config.options.base_url + config.options.endpoints.profile
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}", "Connection": "keep-alive"}
    body = {
        "dataset_id": config.options.dataset_id
    }
    return url, headers, body
