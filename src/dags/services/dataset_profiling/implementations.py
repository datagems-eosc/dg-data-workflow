import json
from datetime import datetime
from typing import Any

from airflow.sdk import Context
from dateutil import parser as date_parser

from common.enum import ConnectorType, DataStoreKind
from common.types.profiled_dataset import DatasetResponse
from configurations import DatasetDiscoveryConfig, DataModelManagementConfig, GatewayConfig, ProfilerConfig
from services.graphs.analytical_pattern_parser import AnalyticalPatternParser


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
                "date_published": date_parser.parse(dag_context["params"]["date_published"]).strftime("%d-%m-%Y"),
                "cite_as": dag_context["params"]["citeAs"],
                "uploaded_by": dag_context["params"]["userId"],
                "data_connectors": [
                    {
                        "type": DataStoreKind(dag_context["params"]["data_store_kind"]).to_connector_type().value,
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
    obj = DatasetResponse.model_validate(json.loads(stringified_profile_data))
    payload = AnalyticalPatternParser().gen_update_dataset(obj, utc_now)
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
