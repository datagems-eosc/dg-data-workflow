import time

from services.logger import Logger


class BaseAuthService:
    def __init__(self, client_id, client_secret, url, scope):
        self.logger = Logger()
        self.client_id = client_id
        self.client_secret = client_secret
        self.url = url
        self.scope = scope
        self._access_token: str | None = None
        self._expires_at: float = 0

    def _login(self) -> dict:
        """To be implemented by subclasses."""
        raise NotImplementedError

    def get_token(self) -> str:
        now = time.time()
        if not self._access_token or now >= self._expires_at:
            token_data = self._login()
            self._access_token = token_data["access_token"]
            expires_in = token_data.get("expires_in", 300)
            self._expires_at = now + expires_in - 10
        return self._access_token
