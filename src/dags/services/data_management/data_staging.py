import os
from io import IOBase


class DataStagingService:
    """
    Handles dataset staging into S3 based on its dataLocation.
    Supports 'http' kind (streaming-safe).
    """

    def __init__(self):
        pass

    def store(self, stream: IOBase, destination_path: str, decode: bool = False) -> str:
        """
        Stores a binary file stream to a local file path.

        :param stream: A binary file-like object (e.g., io.BytesIO, open(file, 'rb')).
        :param destination_path: Destination file path.
        :return: The full path where the file was stored.
        """
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        with open(destination_path, "wb") as f:
            f.write(stream.read(decode_content=decode))
        return os.path.abspath(destination_path)
