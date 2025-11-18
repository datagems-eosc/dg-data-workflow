import os
import uuid
from pathlib import Path

from common.enum.data_location_kind import DataLocationKind
from common.types.data_location import DataLocation
from configurations.workflows_dataset_onboarding_config import DatasetOnboardingConfig
from services.data_management.data_retriever import DataRetriever
from services.data_management.data_staging import DataStagingService
from services.logging.logger import Logger


def build_file_path(directory: str, guid: str, name: str, extension: str | None = None) -> Path:
    if extension:
        ext = extension if extension.startswith(".") else f".{extension}"
        filename = f"{name}{ext}"
    else:
        filename = name

    return Path(directory) / guid / filename

def process_location(guid: str, location: DataLocation, stream_service: DataRetriever,
                     stage_service: DataStagingService, log: Logger,
                     config: DatasetOnboardingConfig) -> DataLocation | bool:
    if location.kind == DataLocationKind.File or location.kind == DataLocationKind.Remote:
        return location
    try:
        with stream_service.retrieve(location) as retrieved_file:
            base_name = Path(retrieved_file.file_name).stem
            extension = retrieved_file.file_extension
            unique_name = f"{base_name}.{uuid.uuid4()}"
            full_path = os.fspath(build_file_path(config.local_staging_path, guid, unique_name, extension))

            stage_service.store(retrieved_file.stream, full_path)
            return DataLocation(DataLocationKind.File, full_path)
    except Exception as e:
        log.error(str(e))
        return False

def extract_directory_path(full_file_path: str):
    return os.path.dirname(full_file_path)