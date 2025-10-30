from airflow.sdk import Variable

from config.aai_core_config import AAICoreConfig
from config.base_config import BaseConfig


class ProfilerConfig(BaseConfig):
    class ProfilerCoreConfig:
        class ProfilerConfig:
            def __init__(self, data: dict):
                self.trigger_profile = data["trigger_profile"]
                self.job_status = data["job_status"]
                self.get_profile = data["get_profile"]

        def __init__(self, data: dict):
            self.base_url = data.get("base_url")
            self.scope = data.get("scope")
            self.profiler = self.ProfilerConfig(data.get("profiler"))

    def __init__(self):
        super().__init__("variables_dev.json")
        self.login_client_id = Variable.get("dwo_aai_clientid")
        self.login_client_password = Variable.get("dwo_aai_clientsecret")
        aai_core = AAICoreConfig(self._configuration_file_data.get("aai"))
        self.login_url = aai_core.base_url
        self.options = self.ProfilerCoreConfig(self._configuration_file_data.get("gateway"))
