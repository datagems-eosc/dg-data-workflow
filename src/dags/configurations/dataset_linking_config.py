from airflow.sdk import Variable

from configurations.aai_core_config import AAICoreConfig


class DatasetLinkingConfig:
    class DatasetLinkingCoreConfig:
        class EndpointsConfig:
            def __init__(self, data: dict):
                self.start_report = data["start_report"]
                self.start_refine = data["start_refine"]
                self.job_status = data["job_status"]
                self.job_result = data["job_result"]

        def __init__(self, data: dict):
            self.base_url = data.get("base_url")
            self.scope = data.get("scope")
            self.report_poke_interval = data.get("report_poke_interval")
            self.refine_poke_interval = data.get("refine_poke_interval")
            self.endpoints = self.EndpointsConfig(data.get("endpoints"))

    def __init__(self):
        self.login_client_id = Variable.get("dwo_aai_clientid")
        self.login_client_password = Variable.get("dwo_aai_clientsecret")
        aai_core = AAICoreConfig(Variable.get("aai", deserialize_json=True))
        self.login_url = aai_core.base_url
        self.options = self.DatasetLinkingCoreConfig(Variable.get("dataset_linking", deserialize_json=True))


