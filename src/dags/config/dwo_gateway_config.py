from utils.configurations import get as fetch


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
        self.login_client_id = fetch("dwo_aai_clientid")
        self.login_client_password = fetch("dwo_aai_clientsecret")
        aai_core = AAICoreConfig(fetch("aai", composite=True))
        self.login_url = aai_core.base_url
        self.options = self.GatewayCoreConfig(fetch("gateway", composite=True))


class AAICoreConfig:
    def __init__(self, data: dict):
        self.base_url = data.get("base_url")
