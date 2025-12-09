from enum import Enum


class ConnectorType(Enum):
    RawDataPath = "RawDataPath"
    DatabaseConnection = "DatabaseConnection"

class DataStoreKind(Enum):
    FileSystem = 0
    RelationalDatabase = 1

    def to_connector_type(self) -> ConnectorType:
        mapping = {
            DataStoreKind.FileSystem: ConnectorType.RawDataPath,
            DataStoreKind.RelationalDatabase: ConnectorType.DatabaseConnection,
        }
        try:
            return mapping[self]
        except KeyError as e:
            raise ValueError(f"No ConnectorType mapping for {self}") from e