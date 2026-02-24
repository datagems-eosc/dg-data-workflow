import uuid
from typing import Any

from airflow.sdk import Context

from common.enum import AnalyticalPatternNodeStatus
from common.extensions.file_extensions import get_staged_path, normalize_s3_path
from common.types import DataLocation
from configurations import GatewayConfig
from services.graphs import AnalyticalPatternParser


def request_onboarding_builder(auth_token: str, dag_context: Context, config: GatewayConfig,
                               data_locations: list[DataLocation]) -> tuple[str, dict[str, str], dict[str | Any, Any]]:
    gateway_url: str = config.options.base_url + config.options.dataset.onboarding_mock
    payload = {
        "Id": dag_context["params"]["id"],
        "Code": dag_context["params"]["code"],
        "Name": dag_context["params"]["name"],
        "Description": dag_context["params"]["description"],
        "Headline": dag_context["params"]["headline"],
        "FieldOfScience": dag_context["params"]["fields_of_science"],
        "Language": dag_context["params"]["languages"],
        "Keywords": dag_context["params"]["keywords"],
        "Country": dag_context["params"]["countries"],
        "Url": dag_context["params"]["publishedUrl"],
        "License": dag_context["params"]["license"],
        "Size": dag_context["params"]["size"],
        "DataLocations": [loc.to_dict() for loc in data_locations],
        "Version": dag_context["params"]["version"],
        "MimeType": dag_context["params"]["mime_type"],
        "DatePublished": dag_context["params"]["date_published"],
        "ConformsTo": dag_context["params"]["conformsTo"],
        "CiteAs": dag_context["params"]["citeAs"]
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}", "Connection": "keep-alive"}
    return gateway_url, headers, payload


def register_dataset_builder(access_token, dag_context, dmm_config, data_locations, utc_now) -> tuple[
    str, dict[str, str], dict[str, Any]]:
    payload = AnalyticalPatternParser().gen_register_dataset({
        "analytical_pattern_node_id": uuid.uuid4(),
        "dmm_operator_node_id": uuid.uuid4(),
        "published_date": utc_now.strftime("%Y-%m-%d"),
        "start_time": utc_now.strftime("%H:%M:%S"),
        "dataset_archived_at": normalize_s3_path(get_staged_path(dag_context["params"]["id"])),
        "dataset_node_id": dag_context["params"]["id"],
        "dataset_cite_as": dag_context["params"]["citeAs"],
        "dataset_conforms_to": dag_context["params"]["conformsTo"],
        "dataset_country": dag_context["params"]["countries"][0],
        "dataset_date_published": dag_context["params"]["date_published"],
        "dataset_description": dag_context["params"]["description"],
        "dataset_fields_of_science": dag_context["params"]["fields_of_science"],
        "dataset_headline": dag_context["params"]["headline"],
        "dataset_languages": dag_context["params"]["languages"],
        "dataset_keywords": dag_context["params"]["keywords"],
        "dataset_license": dag_context["params"]["license"],
        "dataset_name": dag_context["params"]["name"],
        "dataset_url": dag_context["params"]["publishedUrl"],
        "dataset_version": dag_context["params"]["version"],
        "user_node_id": uuid.uuid4(),
        "user_id": dag_context["params"]["userId"],
        "task_node_id": uuid.uuid4(),
        "analytical_pattern_node_status": AnalyticalPatternNodeStatus.STAGED.value
    })
    url: str = dmm_config.options.base_url + dmm_config.options.dataset.register
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}",
               "Connection": "keep-alive"}
    return url, headers, payload


def load_dataset_builder(access_token, dag_context, dmm_config, data_locations, utc_now) -> tuple[
    str, dict[str, str], dict[str, Any]]:
    payload = AnalyticalPatternParser().gen_load_dataset({
        "dataset_node_id": dag_context["params"]["id"],
        "analytical_pattern_node_id": uuid.uuid4(),
        "dmm_operator_node_id": uuid.uuid4(),
        "published_date": utc_now.strftime("%d-%m-%Y"),
        "start_time": utc_now.strftime("%H:%M:%S"),
        "dataset_archived_at": normalize_s3_path(get_staged_path(dag_context["params"]["id"])),
        "user_node_id": uuid.uuid4(),
        "user_id": dag_context["params"]["userId"],
        "task_node_id": uuid.uuid4(),
        "analytical_pattern_node_status": AnalyticalPatternNodeStatus.STAGED.value
    })
    url: str = dmm_config.options.base_url + dmm_config.options.dataset.load
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}",
               "Connection": "keep-alive"}
    return url, headers, payload
