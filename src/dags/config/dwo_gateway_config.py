from airflow.sdk import Variable

from config.aai_core_config import AAICoreConfig


class GatewayConfig:
    class GatewayCoreConfig:
        class DatasetConfig:
            def __init__(self, data: dict):
                self.onboarding_mock = data["onboarding_mock"]
                self.profiling_mock = data["profiling_mock"]

        def __init__(self, data: dict):
            self.base_url = data.get("base_url")
            self.scope = data.get("scope")
            self.dataset = self.DatasetConfig(data.get("dataset"))

    def __init__(self):
        self.login_client_id = Variable.get("dwo_aai_clientid")
        self.login_client_password = Variable.get("dwo_aai_clientsecret")
        aai_core = AAICoreConfig(Variable.get("aai", deserialize_json=True))
        self.login_url = aai_core.base_url
        self.options = self.GatewayCoreConfig(Variable.get("gateway", deserialize_json=True))


