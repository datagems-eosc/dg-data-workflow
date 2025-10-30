from config.dwo_gateway_config import GatewayConfig
from utils.http_requests import http_post
from .base_auth_service import BaseAuthService


class DwoGatewayAuthService(BaseAuthService):
    def __init__(self):
        self.config = GatewayConfig()
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
