from typing import Any

from airflow.sdk import Context
from configurations import DatasetLinkingConfig


def trigger_report_builder(auth_token: str, dag_context: Context, config: DatasetLinkingConfig) -> tuple[
    str, dict[str, str], dict[str, dict[str | Any, Any] | bool]]:
    url: str = config.options.base_url + config.options.endpoints.start_report
    payload = { }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}", "Connection": "keep-alive"}
    return url, headers, payload


def wait_for_completion_builder(auth_token: str, dag_context: Context, config: DatasetLinkingConfig, job_id: str) -> \
        tuple[str, dict[str, str]]:
    url: str = config.options.base_url + config.options.endpoints.job_status.format(id=job_id)
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}", "Connection": "keep-alive"}
    return url, headers