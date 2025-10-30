import ftplib
import tempfile
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from services.logger import Logger
from utils.http_requests import http_get_raw


@dataclass
class RetrievedFile:
    stream: Any
    file_name: str
    file_extension: str


class DataRetriever:
    """
    DataRetriever: a streaming-safe retriever service for large datasets.

    - All methods return file-like *binary* streams.
    - No method buffers the full file in memory.
    - Access token is injected externally (no auth handled here).
    """

    def __init__(self, access_token: str | None = None, *, http_timeout: int = 60):
        self.access_token = access_token
        self.http_timeout = http_timeout
        self.logger = Logger()

    def retrieve_http(self, url: str) -> RetrievedFile:
        """
        Stream a remote HTTP(S) file.

        Returns:
            urllib3.response.HTTPResponse (file-like stream)
        """
        headers = {}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        response = http_get_raw(url, headers=headers)
        parsed = urlparse(url)
        file_name = Path(parsed.path).name or "downloaded_file"
        file_extension = Path(file_name).suffix.lstrip(".")
        return RetrievedFile(closing(response), file_name, file_extension)

    def retrieve_ftp(self, url: str) -> RetrievedFile:
        """
        Stream a file from an FTP server using a temporary on-disk file.
        Avoids buffering entire content in memory.
        """
        parsed = urlparse(url)
        if parsed.scheme != "ftp":
            raise ValueError(f"Invalid FTP URL: {url}")

        username = parsed.username or "anonymous"
        password = parsed.password or ""

        temp_file = tempfile.SpooledTemporaryFile(max_size=0, mode="w+b")

        with ftplib.FTP(parsed.hostname) as ftp:
            ftp.login(user=username, passwd=password)
            ftp.retrbinary(f"RETR {parsed.path}", temp_file.write)

        temp_file.seek(0)
        file_name = Path(parsed.path).name or "ftp_file"
        file_extension = Path(file_name).suffix.lstrip(".")
        return RetrievedFile(closing(temp_file), file_name, file_extension)

    def retrieve_file(self, path: str) -> RetrievedFile:
        """
        Open a local file or S3 object and return a streaming handle.
        """
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        stream = open(file_path, "rb")
        file_name = file_path.name
        file_extension = file_path.suffix.lstrip(".")
        return RetrievedFile(closing(stream), file_name, file_extension)

    def retrieve(self, kind: str, url_or_path: str) -> RetrievedFile | None:
        """
        Convenience wrapper that picks the right retriever.
        """
        result = None
        match kind.lower():
            case "http":
                result = self.retrieve_http(url_or_path)
            case "ftp":
                result = self.retrieve_ftp(url_or_path)
            case "file" | "remote":
                result = self.retrieve_file(url_or_path)
            case _:
                raise ValueError(f"Unsupported dataLocation.kind: {kind}")
        return result
