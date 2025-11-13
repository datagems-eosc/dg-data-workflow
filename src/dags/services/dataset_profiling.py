import datetime
from typing import Any

from airflow.sdk import Context, Param
from dateutil import parser as date_parser

from common.enum.connector_type import ConnectorType
from configurations.cross_dataset_discovery_indexing_config import DatasetDiscoveryConfig
from configurations.dwo_gateway_config import GatewayConfig
from configurations.workflows_dataset_profiler_config import ProfilerConfig

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
    "version": Param(type="string"),
    "headline": Param("", type="string"),
    "keywords": Param([], type="array"),
    "fields_of_science": Param([], type="array"),
    "languages": Param([], type="array"),
    "countries": Param([], type="array"),
    "date_published": Param(f"{datetime.date.today()}", type="string", format="date"),
    "dataset_file_path": Param("", type="string"),
}

DAG_TAGS = ["DatasetProfiling", ]
DAG_DISPLAY_NAME = "Dataset Profiling"
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
                "cite_as": "foo",  # TODO: get it from backend
                "uploaded_by": "ADMIN",  # TODO: get it from backend
                "dataset_file_path": dag_context["params"]["dataset_file_path"],
                "data_connectors": [
                    {
                        "type": ConnectorType.RawDataPath.value,
                        # TODO: keep track for when there is logic for getting a specific connector
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


def profile_cleanup_builder(auth_token: str, dag_context: Context, config: ProfilerConfig, profile_id: str):
    url: str = config.options.base_url + config.options.profiler.cleanup
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}",
               "Connection": "keep-alive"}
    payload = {
        "profile_job_id": profile_id
    }
    return url, headers, payload
