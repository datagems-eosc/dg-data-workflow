from dataclasses import dataclass
from typing import Any


@dataclass
class RetrievedFile:
    stream: Any
    file_name: str
    file_extension: str

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        try:
            if self.stream:
                if hasattr(self.stream, "__exit__"):
                    self.stream.__exit__(exc_type, exc_val, exc_tb)
                elif hasattr(self.stream, "close"):
                    self.stream.close()
        except Exception:
            pass
