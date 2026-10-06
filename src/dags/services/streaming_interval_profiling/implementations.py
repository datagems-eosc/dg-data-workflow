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


def upsert_moma_builder(config: DataModelManagementConfig, auth_token: str,
                        streaming_profiler_response: str) -> tuple[str, dict[str, str], dict[str, Any]]:
    url: str = config.options.base_url + config.options.dataset.update
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}", "Connection": "keep-alive"}

    obj = json.loads(streaming_profiler_response)
    payload = AnalyticalPatternParser().gen_update_dataset_streaming(obj["datasetId"], datetime.now(timezone.utc))
    nodes = [
                {"id": x["nodeId"], "properties": x["properties"]}
                for x in obj["momaUpdates"]
            ] + obj["momaCreates"][0]["nodes"]
    edges = obj["momaCreates"][0]["edges"]
    payload["ap"]["nodes"].extend(nodes)
    payload["ap"]["edges"].extend(edges)

    return url, headers, payload
