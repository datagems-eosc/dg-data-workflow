import json
from datetime import datetime
from typing import Any

from airflow.sdk import Context
from dateutil import parser as date_parser

from common.enum import DataStoreKind, MomaProfileType
from common.types.profiled_dataset import DatasetResponse
from configurations import DatasetDiscoveryConfig, DataModelManagementConfig, GatewayConfig, ProfilerConfig, \
    MomaManagementConfig
from services.graphs import AnalyticalPatternParser


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
                "date_published": date_parser.parse(dag_context["params"]["date_published"]).strftime("%Y-%m-%d"),
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


def convert_profiling_builder(access_token: str, dag_context: Context,
                              moma_config: MomaManagementConfig, stringified_profile_data: str, profile_type: str) -> \
        tuple[str, dict[str, str], Any]:
    url: str = moma_config.options.base_url + (
        moma_config.options.convert.light if profile_type is MomaProfileType.LIGHT.value else moma_config.options.convert.heavy)
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}",
               "Connection": "keep-alive"}
    payload = json.loads(stringified_profile_data)[profile_type]
    return url, headers, payload


def update_data_model_management_builder(access_token: str, dag_context: Context,
                                         dmm_config: DataModelManagementConfig, converted_profile_json: str, original_profile: str,
                                         utc_now: datetime, profile_type: str) -> tuple[
    str, dict[str, str], dict[str, Any]]:
    obj = DatasetResponse.model_validate(json.loads(original_profile)[profile_type])
    payload = AnalyticalPatternParser().gen_update_dataset(obj, utc_now)
    converted_profile = json.loads(converted_profile_json)
    payload["nodes"].extend(converted_profile["metadata"]["nodes"])
    payload["edges"].extend(converted_profile["metadata"]["edges"])
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
