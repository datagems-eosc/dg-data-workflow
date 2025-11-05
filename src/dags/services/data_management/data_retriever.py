import ftplib
import tempfile
from pathlib import Path
from urllib.parse import urlparse

from common.enum.data_location_kind import DataLocationKind
from common.extensions.http_requests import http_get_raw
from common.types.data_location import DataLocation
from common.types.retrieved_file import RetrievedFile
from services.logging.logger import Logger

DEFAULT_FILE_NAME = "downloaded_file"
MAX_FILE_NAME_LENGTH = 255

class DataRetriever:
    """
    DataRetriever: a streaming-safe retriever service for large datasets.

    - All methods return file-like *binary* streams.
    - No method buffers the full file in memory.
    - Access token is injected externally (no authorization handled here).
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
        file_name = Path(parsed.path).name or DEFAULT_FILE_NAME
        if len(file_name) > MAX_FILE_NAME_LENGTH:
            file_name = DEFAULT_FILE_NAME
        file_extension = Path(file_name).suffix.lstrip(".")
        return RetrievedFile(response, file_name, file_extension)

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
        return RetrievedFile(temp_file, file_name, file_extension)

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
        return RetrievedFile(stream, file_name, file_extension)

    def retrieve(self, data_location: DataLocation) -> RetrievedFile | None:
        """
        Convenience wrapper that picks the right retriever.
        """
        result = None
        match data_location.kind:
            case DataLocationKind.Http:
                result = self.retrieve_http(data_location.url)
            case DataLocationKind.Ftp:
                result = self.retrieve_ftp(data_location.url)
            case DataLocationKind.File | DataLocationKind.Remote:
                result = self.retrieve_file(data_location.url)
            case _:
                raise ValueError(f"Unsupported dataLocation.kind: {data_location.kind}")
        return result
