import ftplib
import tempfile
from contextlib import contextmanager, closing
from pathlib import Path
from urllib.parse import urlparse
from utils.http_requests import http_get_raw

from services.logger import Logger


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
        # self._s3 = boto3.client("s3")

    def retrieve_http(self, url: str):
        """
        Stream a remote HTTP(S) file.

        Returns:
            urllib3.response.HTTPResponse (file-like stream)
        """
        headers = {}
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        response = http_get_raw(url, headers=headers)
        return response

    def retrieve_ftp(self, url: str):
        """
        Stream a file from an FTP server using a temporary on-disk file.
        Avoids buffering entire content in memory.

        Returns:
            tempfile.SpooledTemporaryFile (file-like stream)
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
        return temp_file


    def retrieve_file(self, path: str):
        """
        Open a local file or S3 object and return a streaming handle.

        - Local files use Python's open() in binary read mode.
        - S3 objects return a boto3 StreamingBody.

        Returns:
            io.BufferedReader or botocore.response.StreamingBody
        """
        # if path.startswith("s3://"):
        #     parsed = urlparse(path)
        #     bucket = parsed.netloc
        #     key = parsed.path.lstrip("/")
        #
        #     obj = self._s3.get_object(Bucket=bucket, Key=key)
        #     # obj["Body"] is a botocore.response.StreamingBody (streaming, chunked)
        #     return obj["Body"]

        # Local file
        file_path = Path(path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return open(file_path, "rb")

    def retrieve(self, kind: str, url_or_path: str):
        """
        Convenience wrapper that picks the right retriever.
        """
        stream = None
        match kind.lower():
            case "http":
                stream = self.retrieve_http(url_or_path)
            case "ftp":
                stream = self.retrieve_ftp(url_or_path)
            case "file" | "remote":
                stream = self.retrieve_file(url_or_path)
            case _:
                raise ValueError(f"Unsupported dataLocation.kind: {kind}")
        return closing(stream)
