import uuid
from datetime import date
from typing import Any

from airflow.sdk import Context, Param

from common.types.analytical_pattern_edge import AnalyticalPatternEdge
from common.types.analytical_pattern_node import AnalyticalPatternNode
from common.types.data_location import DataLocation
from configurations.dwo_gateway_config import GatewayConfig
from services.graphs.analytical_pattern_parser import AnalyticalPatternParser

DAG_ID = "DATASET_ONBOARDING"

DAG_PARAMS = {
    "id": Param("00000000-0000-0000-0000-000000000000", type="string", format="uuid"),
    "code": Param(type="string"), "name": Param(type="string"),
    "description": Param(type="string"),
    "headline": Param(type="string"),
    "fields_of_science": Param([], type="array"),
    "languages": Param([], type="array"),
    "keywords": Param([], type="array"),
    "countries": Param([], type="array"),
    "publishedUrl": Param(type="string", format="uri"),
    "doi": Param(type="string", format="uri"),
    "citeAs": Param("", type="string"),
    "license": Param(type="string"),
    "size": Param(type="integer", minimum=0),
    "dataLocations": Param([], type="string"),
    "version": Param(type="string"),
    "mime_type": Param(type="string"),
    "date_published": Param(f"{date.today()}", type="string", format="date"),
    "userId": Param(type="string")
}

DAG_TAGS = ["DatasetOnboarding", ]


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
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}", "Connection": "keep-alive"}
    return gateway_url, headers, payload


def register_dataset_builder(access_token, dag_context, dmm_config, data_locations, utc_now) -> tuple[
    str, dict[str, str], dict[str, Any]]:
    payload = AnalyticalPatternParser().gen_register_dataset({
        "analytical_pattern_node_id": uuid.uuid4(),
        "dmm_operator_node_id": uuid.uuid4(),
        "published_date": utc_now.strftime("%d-%m-%Y"),
        "start_time": utc_now.strftime("%H:%M:%S"),
        "dataset_archived_at": data_locations[0].url,
        "dataset_node_id": dag_context["params"]["id"],
        "dataset_cite_as": "",  # TODO
        "dataset_conforms_to": "",  # TODO
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
        "UserId": dag_context["params"]["userId"],
        "task_node_id": uuid.uuid4()
    })
    url: str = dmm_config.options.base_url + dmm_config.options.dataset.register
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}",
               "Connection": "keep-alive"}
    return url, headers, payload


def load_dataset_builder(access_token, dag_context, dmm_config, data_locations, utc_now) -> tuple[
    str, dict[str, str], dict[str, list[AnalyticalPatternEdge] | list[AnalyticalPatternNode]]]:
    payload = AnalyticalPatternParser().gen_load_dataset({
        "analytical_pattern_node_id": uuid.uuid4(),
        "dmm_operator_node_id": uuid.uuid4(),
        "published_date": utc_now.strftime("%d-%m-%Y"),
        "start_time": utc_now.strftime("%H:%M:%S"),
        "dataset_archived_at": data_locations[0].url,
        "dataset_node_id": dag_context["params"]["id"],
        "dataset_cite_as": "",  # TODO
        "dataset_conforms_to": "",  # TODO
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
        "UserId": dag_context["params"]["userId"],
        "task_node_id": uuid.uuid4()
    })
    url: str = dmm_config.options.base_url + dmm_config.options.dataset.load
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {access_token}",
               "Connection": "keep-alive"}
    return url, headers, payload
