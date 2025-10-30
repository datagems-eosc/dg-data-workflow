from config.base_config import BaseConfig


class DatasetOnboardingConfig(BaseConfig):
    def __init__(self):
        super().__init__("variables_dev.json")
        self.local_staging_path = self._configuration_file_data.get("local_staging_path")
