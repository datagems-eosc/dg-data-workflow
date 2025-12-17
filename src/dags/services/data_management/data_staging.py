import os
from io import IOBase


class DataStagingService:

    def __init__(self):
        pass

    def store(self, stream: IOBase, destination_path: str, decode: bool = False) -> str:
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        with open(destination_path, "wb") as f:
            f.write(stream.read(decode_content=decode))
        return os.path.abspath(destination_path)
