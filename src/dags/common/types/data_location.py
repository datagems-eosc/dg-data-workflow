from dataclasses import dataclass

from common.enum import DataLocationKind

@dataclass
class DataLocation:
    kind : DataLocationKind = DataLocationKind.File
    location: str | None = None

    @classmethod
    def from_dict(cls, data: dict):
        kind_value = data.get("kind")
        if isinstance(kind_value, int):
            kind = DataLocationKind(kind_value)
        elif isinstance(kind_value, str):
            kind = DataLocationKind[kind_value]
        else:
            raise ValueError(f"Invalid kind value: {kind_value}")
        return cls(kind=kind, location=data.get("location"))

    def to_dict(self) -> dict[str, int | str | None]:
        return {
            "kind": self.kind.value,  # convert Enum to int
            "location": self.location,
        }
