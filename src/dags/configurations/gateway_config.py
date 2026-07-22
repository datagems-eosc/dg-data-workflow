from airflow.sdk import Variable

from configurations.aai_core_config import AAICoreConfig


class GatewayConfig:
    class GatewayCoreConfig:
        class DatasetConfig:
            def __init__(self, data: dict):
                self.process_step_update = data["process_step_update"]

        def __init__(self, data: dict):
            self.base_url = data.get("base_url")
            self.scope = data.get("scope")
            self.endpoints = self.DatasetConfig(data.get("endpoints"))

    def __init__(self):
        self.login_client_id = Variable.get("dwo_aai_clientid")
        self.login_client_password = Variable.get("dwo_aai_clientsecret")
        aai_core = AAICoreConfig(Variable.get("aai", deserialize_json=True))
        self.login_url = aai_core.base_url
        self.options = self.GatewayCoreConfig(Variable.get("gateway", deserialize_json=True))


