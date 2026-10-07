import json
from datetime import datetime, timezone
from typing import Any

from airflow.sdk import Context

from configurations import StreamingIntervalProfilerConfig, DataModelManagementConfig
from services.graphs import AnalyticalPatternParser


def fetch_profile_builder(config: StreamingIntervalProfilerConfig, dag_context: Context, auth_token: str) -> tuple[
    str, dict[str, str], dict[str, Any | None]]:
    url: str = config.options.base_url + config.options.endpoints.profile
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}", "Connection": "keep-alive"}
    body = {
        "dataset_id": config.options.dataset_id
    }
    return url, headers, body

def fetch_moma_builder(config: DataModelManagementConfig, auth_token: str, streaming_profiler_response: str):
    obj = json.loads(streaming_profiler_response)
    url: str = config.options.base_url + config.options.dataset.get.format(id=obj["datasetId"])
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}", "Connection": "keep-alive"}
    return url, headers


def upsert_moma_builder(config: DataModelManagementConfig, auth_token: str,
                        streaming_profiler_response: str, fetch_response: Any) -> tuple[str, dict[str, str], dict[str, Any]]:
    url: str = config.options.base_url + config.options.dataset.update
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}", "Connection": "keep-alive"}

    obj = json.loads(streaming_profiler_response)
    payload: dict[str, Any] = []
    nodes = [
                {"id": x["nodeId"], "properties": x["properties"]}
                for x in obj["momaUpdates"]
            ] + obj["momaCreates"][0]["nodes"] 
            # + [
            #     next(
            #         node
            #         for node in fetch_response["dataset"]["nodes"]
            #         if "sc:Dataset" in node.get("labels", [])
            #     )
            # ]
    edges = obj["momaCreates"][0]["edges"]
    payload["ap"]["nodes"].extend(nodes)
    payload["ap"]["edges"].extend(edges)

    return url, headers, payload
