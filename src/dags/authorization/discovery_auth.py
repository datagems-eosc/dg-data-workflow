from common.extensions.http_requests import http_post
from configurations.cross_dataset_discovery_indexing_config import DatasetDiscoveryConfig
from .base_auth_service import BaseAuthService


class DiscoveryAuthService(BaseAuthService):
    def __init__(self):
        self.config = DatasetDiscoveryConfig()
        super().__init__(
            client_id=self.config.login_client_id,
            client_secret=self.config.login_client_password,
            url=self.config.login_url,
            scope=self.config.options.scope,
        )

    def _login(self) -> dict:
        return http_post(
            self.url,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "scope": self.scope,
            },
        )
