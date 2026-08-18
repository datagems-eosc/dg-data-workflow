import os
import shutil
from io import IOBase


class DataStagingService:

    def store(self, stream: IOBase, destination_path: str, decode: bool = False, ) -> str:
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)

        with open(destination_path, "wb") as destination:
            if decode:
                content = stream.read(decode_content=True)
                destination.write(content)
            else:
                shutil.copyfileobj(stream, destination)

        return os.path.abspath(destination_path)
