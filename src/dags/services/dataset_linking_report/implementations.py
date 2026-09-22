from typing import Any

from airflow.sdk import Context

from configurations import DatasetLinkingConfig


def trigger_report_builder(auth_token: str, dag_context: Context, config: DatasetLinkingConfig) -> tuple[
    str, dict[str, str], dict[str, Any]]:
    url: str = config.options.base_url + config.options.endpoints.start_report
    payload: dict[str, Any] = {}
    if dag_context["params"].get("kw") is not None:
        payload["kw"] = dag_context["params"]["kw"]
    if dag_context["params"].get("desc") is not None:
        payload["desc"] = dag_context["params"]["desc"]
    if dag_context["params"].get("head") is not None:
        payload["head"] = dag_context["params"]["head"]
    if dag_context["params"].get("th") is not None:
        payload["th"] = dag_context["params"]["th"]
    if dag_context["params"].get("keyword_method"):
        payload["keyword_method"] = dag_context["params"]["keyword_method"]
    if dag_context["params"].get("include_chunks") is not None:
        payload["include_chunks"] = dag_context["params"]["include_chunks"]
    if dag_context["params"].get("include_graphs") is not None:
        payload["include_graphs"] = dag_context["params"]["include_graphs"]
    if dag_context["params"].get("graphs_only_above_threshold") is not None:
        payload["graphs_only_above_threshold"] = dag_context["params"]["graphs_only_above_threshold"]
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}", "Connection": "keep-alive"}
    return url, headers, payload


def wait_for_completion_builder(auth_token: str, dag_context: Context, config: DatasetLinkingConfig, job_id: str) -> \
        tuple[str, dict[str, str]]:
    url: str = config.options.base_url + config.options.endpoints.job_status.format(id=job_id)
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}", "Connection": "keep-alive"}
    return url, headers
