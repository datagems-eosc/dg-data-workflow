from airflow.sdk import Variable

from configurations.aai_core_config import AAICoreConfig


class DatasetDiscoveryConfig:
    class CrossDatasetDiscoveryIndexingCore:
        def __init__(self, data: dict):
            self.base_url = data.get("base_url")
            self.scope = data.get("scope")
            # TODO: add the class and mappings to the endpoints

    def __init__(self):
        self.login_client_id = Variable.get("dwo_aai_clientid")
        self.login_client_password = Variable.get("dwo_aai_clientsecret")
        aai_core = AAICoreConfig(Variable.get("aai", deserialize_json=True))
        self.login_url = aai_core.base_url
        self.options = self.CrossDatasetDiscoveryIndexingCore(
            Variable.get("dataset_discovery", deserialize_json=True))
