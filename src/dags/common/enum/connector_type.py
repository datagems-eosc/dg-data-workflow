from enum import Enum


class ConnectorType(Enum):
    RawDataPath = "RawDataPath"
    DatabaseConnection = "DatabaseConnection"

class DataStoreKind(Enum):
    FileSystem = 0
    RelationalDatabase = 1