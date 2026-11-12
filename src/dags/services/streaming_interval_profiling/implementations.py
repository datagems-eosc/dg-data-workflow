import json
from typing import Any

from airflow.sdk import Context

from configurations import StreamingIntervalProfilerConfig, DataModelManagementConfig


def fetch_profile_builder(config: StreamingIntervalProfilerConfig, dag_context: Context, auth_token: str) -> tuple[
    str, dict[str, str], dict[str, Any | None]]:
    url: str = config.options.base_url + config.options.endpoints.profile
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}", "Connection": "keep-alive"}
    body = {
        "dataset_id": config.options.dataset_id
    }
    return url, headers, body


def fetch_moma_builder(config: DataModelManagementConfig, auth_token: str, streaming_profiler_response: str) -> tuple[
    str, dict[str, str]]:
    obj = json.loads(streaming_profiler_response)
    url: str = config.options.base_url + config.options.dataset.get.format(id=obj["datasetId"])
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}", "Connection": "keep-alive"}
    return url, headers


def upsert_moma_builder(config: DataModelManagementConfig, auth_token: str,
                        streaming_profiler_response: str, fetch_response: Any) -> tuple[
    str, dict[str, str], dict[str, Any]]:
    url: str = config.options.base_url + config.options.dataset.update
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}", "Connection": "keep-alive"}

    obj = json.loads(streaming_profiler_response)
    payload: dict[str, Any] = {
        "ap": fetch_response["dataset"]
    }

    nodes_by_id = {
        node["id"]: node
        for node in payload["ap"]["nodes"]
    }

    for update in obj.get("momaUpdates", []):
        node_id = update["nodeId"]
        nodes_by_id[node_id]["properties"] = update["properties"]

    for creation in obj.get("momaCreates", []):
        payload["ap"]["nodes"].extend(creation["nodes"])
        payload["ap"]["edges"].extend(creation["edges"])

    dataset_node = next(
        (node for node in payload["ap"]["nodes"] if "sc:Dataset" in node.get("labels", [])),
        None
    )
    uploaded_by = (dataset_node or {}).get("properties", {}).get("uploadedBy")
    if uploaded_by and uploaded_by not in nodes_by_id:
        payload["ap"]["nodes"].append({
            "id": uploaded_by,
            "labels": ["User"],
            "properties": {}
        })

    return url, headers, payload
