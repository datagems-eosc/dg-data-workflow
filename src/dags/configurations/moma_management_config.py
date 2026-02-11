from airflow.sdk import Variable

from configurations.aai_core_config import AAICoreConfig


class MomaManagementConfig:
    class MomaManagementCoreConfig:
        class ConvertConfig:
            def __init__(self, data: dict):
                self.light = data["light"]
                self.heavy = data["heavy"]

        def __init__(self, data: dict):
            self.base_url = data.get("base_url")
            self.scope = data.get("scope")
            self.convert = self.ConvertConfig(data.get("convert"))

    def __init__(self):
        self.login_client_id = Variable.get("dwo_aai_clientid")
        self.login_client_password = Variable.get("dwo_aai_clientsecret")
        aai_core = AAICoreConfig(Variable.get("aai", deserialize_json=True))
        self.login_url = aai_core.base_url
        self.options = self.MomaManagementCoreConfig(Variable.get("moma_management", deserialize_json=True))


