import json
from pathlib import Path


class BaseConfig:
    _CONFIGURATION_DIR_PATH = "/opt/airflow/configurations/"
    def __init__(self, file_name: str):
        file_path = Path(self._CONFIGURATION_DIR_PATH + file_name)
        if not file_path.exists():
            raise FileNotFoundError(f"[{file_name} JSON file not found at path: {self._CONFIGURATION_DIR_PATH}")
        with file_path.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError as e:
                raise json.JSONDecodeError(f"[{file_name} Failed to parse JSON: {e.msg}", e.doc, e.pos)
        if not isinstance(data, dict):
            raise TypeError(f"[{file_name}] Expected a JSON object, but got {type(data).__name__}")
        self._configuration_file_data = data

