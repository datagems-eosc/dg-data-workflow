import datetime
import os
import uuid

from airflow.models.param import Param
from airflow.sdk import Context

from config.dwo_gateway_config import GatewayConfig
from config.workflows_dataset_onboarding_config import DatasetOnboardingConfig
from services.data_retriever import DataRetriever
from services.data_staging import DataStagingService
from services.logger import Logger
from utils.file_extensions import build_file_path

DAG_ID = "DATASET_ONBOARDING"

DAG_PARAMS = {
    "id": Param(type="string", format="uuid"),
    "code": Param(type="string"),
    "name": Param(type="string"),
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
    "size": Param(0, type="integer", minimum=0),
    "dataLocations": Param([], type="string"),
    "version": Param(type="string"),
    "mime_type": Param(type="string"),
    "date_published": Param(f"{datetime.date.today()}", type="string", format="date"),

}

DAG_TAGS = ["DatasetOnboarding", ]


def config_onboarding(auth_token: str, dag_context: Context, config: GatewayConfig,
                      data_locations: list[tuple[str, str]]):
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
        "DataLocations": [{"kind": k, "url": u} for k, u in data_locations],
        "Version": dag_context["params"]["version"],
        "MimeType": dag_context["params"]["mime_type"],
        "DatePublished": dag_context["params"]["date_published"],
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}",
               "Connection": "keep-alive"}
    return gateway_url, headers, payload


def process_location(guid: str, location, stream_service: DataRetriever, stage_service: DataStagingService, log: Logger,
                     config: DatasetOnboardingConfig) -> tuple[str, str] | bool:
    kind: str = location["kind"]
    url: str = location["url"]
    if kind.lower() == "file" or kind.lower() == "remote":
        return kind, url
    try:
        with stream_service.retrieve(kind, url) as retrieved_file:
            full_path = os.fspath(
                build_file_path(config.local_staging_path, guid, retrieved_file.file_name + str(uuid.uuid4()),
                                retrieved_file.file_extension))
            stage_service.store(retrieved_file.stream, full_path)
            return kind, full_path
    except Exception as e:
        log.error(e)
        return False
