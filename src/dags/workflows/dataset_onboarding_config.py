import json
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
    "name": Param(type="string"),
    "description": Param(type="string"),
    "headline": Param(type="string"),
    "fields_of_science": Param([], type="array"),
    "languages": Param(["en", "es"], type="array"),
    "keywords": Param([], type="array"),
    "countries": Param([], type="array"),
    "publishedUrl": Param(type="string", format="uri"),
    "doi": Param(type="string", format="uri"),
    "citeAs": Param("", type="string"),
    "license": Param(type="string"),
    "size": Param(0, type="integer", minimum=0),
    "dataLocations": Param(json.dumps(
        [
            {
                "kind": "File",  # other options: http, ftp, remote
                "url": "/opt/airflow/config/folder/train-images.idx3-ubyte"
            },
            {
                "kind": "Ftp",  # other options: http, ftp, remote
                "url": "ftp://my-ftp-server:21/train-images.idx3-ubyte"
            },
            {
                "kind": "Http",  # other options: http, ftp, remote
                "url": "https://tse3.mm.bing.net/th/id/OIP.U_VJuupQohwnzXcKMztqWgHaEo?rs=1&pid=ImgDetMain&o=7&rm=3"
            }
        ]), type="string"),
}

DAG_TAGS = ["DatasetOnboarding", ]


def config_onboarding(auth_token: str, dag_context: Context, config: GatewayConfig):
    gateway_url: str = config.options.base_url + config.options.dataset.onboarding_mock
    payload = {
        "Id": dag_context["params"]["id"],
        "Code": dag_context["params"]["id"],
        "Name": dag_context["params"]["name"],
        "Description": dag_context["params"]["description"],
        "License": dag_context["params"]["license"],
        "MimeType": "my-mime",
        "Size": dag_context["params"]["size"],
        "Url": dag_context["params"]["publishedUrl"],
        "Version": "v1",
        "Headline": dag_context["params"]["headline"],
        "Keywords": dag_context["params"]["keywords"],
        "FieldOfScience": dag_context["params"]["fields_of_science"],
        "Language": dag_context["params"]["languages"],
        "Country": dag_context["params"]["countries"],
        "DatePublished": "2025-10-23"
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {auth_token}",
               "Connection": "keep-alive"}
    return gateway_url, headers, payload


def process_location(location, stream_service: DataRetriever, stage_service: DataStagingService, log: Logger,
                     config: DatasetOnboardingConfig) -> str | bool:
    kind: str = location["kind"]
    url = location["url"]
    if kind.lower() == "file" or kind.lower() == "remote":
        return True
    local_path = f"{config.local_staging_path}{kind}_{abs(hash(url))}.dat"
    try:
        with stream_service.retrieve(kind, url) as retrieved_file:
            full_path = build_file_path(config.local_staging_path, retrieved_file.file_name + str(uuid.uuid4()),
                                        retrieved_file.file_extension)
            stage_service.store(retrieved_file.stream, os.fspath(full_path))
        return local_path
    except Exception as e:
        log.error(e)
        return False
