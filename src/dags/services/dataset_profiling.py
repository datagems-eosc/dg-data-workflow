import json
import uuid
from datetime import datetime, date
from typing import Any

from airflow.sdk import Context, Param
from dateutil import parser as date_parser

from common.enum import ConnectorType
from common.extensions.file_extensions import get_staged_path
from configurations import DatasetDiscoveryConfig, DataModelManagementConfig, GatewayConfig, ProfilerConfig
from services.graphs.analytical_pattern_parser import AnalyticalPatternParser

DAG_ID = "DATASET_PROFILING"
DAG_PARAMS = {
    "id": Param("00000000-0000-0000-0000-000000000000", type="string", format="uuid"),
    "code": Param("", type="string"),
    "name": Param("", type="string"),
    "description": Param("", type="string"),
    "license": Param("", type="string"),
    "mime_type": Param("", type="string"),
    "size": Param(0, type="integer", minimum=0),
    "url": Param("", type="string", format="uri"),
    "version": Param("", type="string"),
    "headline": Param("", type="string"),
    "keywords": Param([], type="array"),
    "fields_of_science": Param([], type="array"),
    "languages": Param([], type="array"),
    "countries": Param([], type="array"),
    "date_published": Param(f"{date.today()}", type="string", format="date"),
    "dataset_file_path": Param("", type="string"),
    "userId": Param("", type="string"),
    "citeAs": Param("", type="string"),
    "conformsTo": Param("", type="string"),
}

DAG_TAGS = ["DatasetProfiling", ]

WAIT_FOR_COMPLETION_POKE_INTERVAL = ProfilerConfig().options.profiler.poke_interval


def trigger_profile_builder(auth_token: str, dag_context: Context, config: ProfilerConfig, is_light_profile: bool) -> \
        tuple[
            str, dict[str, str], dict[str, dict[str | Any, Any] | bool]]:
    profiler_url: str = config.options.base_url + \
                        config.options.profiler.trigger_profile

    payload = {
        "profile_specification":
            {
                "id": dag_context["params"]["id"],
                "name": dag_context["params"]["name"],
                "description": dag_context["params"]["description"],
                "license": dag_context["params"]["license"],
                "published_url": dag_context["params"]["url"],
                "headline": dag_context["params"]["headline"],
                "keywords": dag_context["params"]["keywords"],
                "fields_of_science": dag_context["params"]["fields_of_science"],
                "languages": dag_context["params"]["languages"],
                "country": dag_context["params"]["countries"][0],
                "date_published": date_parser.parse(dag_context["params"]["date_published"]).strftime("%m-%d-%Y"),
                "cite_as": dag_context["params"]["citeAs"],
                "uploaded_by": dag_context["params"]["userId"],
                "data_connectors": [
                    {
                        "type": ConnectorType.RawDataPath.value,
                        "dataset_id": dag_context["params"]["id"]
                    }
                ]
            },
        "only_light_profile": is_light_profile
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}",
               "Connection": "keep-alive"}
    return profiler_url, headers, payload


def wait_for_completion_builder(auth_token: str, dag_context: Context, config: ProfilerConfig, profile_id: str) -> \
        tuple[str, dict[str, str]]:
    url: str = config.options.base_url + \
               config.options.profiler.job_status.format(id=profile_id)
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}",
               "Connection": "keep-alive"}
    return url, headers


def fetch_profile_builder(auth_token: str, dag_context: Context, config: ProfilerConfig, profile_id: str) -> tuple[
    str, dict[str, str]]:
    url: str = config.options.base_url + \
               config.options.profiler.get_profile.format(id=profile_id)
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}",
               "Connection": "keep-alive"}
    return url, headers


def update_data_management_builder(auth_token: str, dag_context: Context, config: GatewayConfig,
                                   stringified_profile_data: str) -> tuple[str, dict[str, str], str]:
    url: str = config.options.base_url + config.options.dataset.profiling_mock.format(
        id=dag_context["params"]["id"]) + "?f=Id"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}",
               "Connection": "keep-alive"}
    return url, headers, stringified_profile_data


def update_data_model_management_builder(access_token: str, dag_context: Context,
                                         dmm_config: DataModelManagementConfig, stringified_profile_data: str,
                                         utc_now: datetime) -> tuple[str, dict[str, str], dict[str, Any]]:
    payload = AnalyticalPatternParser().gen_update_dataset({
        "analytical_pattern_node_id": str(uuid.uuid4()),
        "published_date": utc_now.strftime("%d-%m-%Y"),
        "start_time": utc_now.strftime("%H:%M:%S"),
        "dmm_operator_node_id": str(uuid.uuid4()),
        "payload": json.loads(stringified_profile_data),
        "dataset_node_id": dag_context["params"]["id"],
        "dataset_archived_at": get_staged_path(dag_context["params"]["id"]),
        "dataset_archived_by": dag_context["params"]["userId"],  # TODO: this is probs the onboarding action's user
        "dataset_cite_as": dag_context["params"]["citeAs"],
        "dataset_conforms": dag_context["params"]["conformsTo"],
        "file_object_node_id": str(uuid.uuid4()),
        "user_node_id": str(uuid.uuid4()),
        "user_user_id": dag_context["params"]["userId"],
        "task_node_id": str(uuid.uuid4())
    })
    url: str = dmm_config.options.base_url + dmm_config.options.dataset.update
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}",
               "Connection": "keep-alive"}
    return url, headers, payload


def pass_index_files_builder(auth_token: str, dag_context: Context, config: DatasetDiscoveryConfig,
                             stringified_profile_data: str) -> tuple[str, dict[str, str], dict[str, str]]:
    # TODO: this method should be implemented when the cross dataset discovery is
    url: str = config.options.base_url + config.options.dataset.insert
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}",
               "Connection": "keep-alive"}
    payload = {
        "data_placeholder": stringified_profile_data
    }
    return url, headers, payload


def profile_cleanup_builder(auth_token: str, dag_context: Context, config: ProfilerConfig, profile_id: str) -> tuple[
    str, dict[str, str], dict[str, str]]:
    url: str = config.options.base_url + config.options.profiler.cleanup
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}",
               "Connection": "keep-alive"}
    payload = {
        "profile_job_id": profile_id
    }
    return url, headers, payload
