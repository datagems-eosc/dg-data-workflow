from common.enum.data_location_kind import DataLocationKind


class DataLocation:
    def __init__(self, kind: DataLocationKind = DataLocationKind.File, url: str | None = None):
        self.kind = kind
        self.url = url

    @classmethod
    def from_dict(cls, data: dict):
        kind_value = data.get("kind")
        if isinstance(kind_value, int):
            kind = DataLocationKind(kind_value)
        elif isinstance(kind_value, str):
            kind = DataLocationKind[kind_value]
        else:
            raise ValueError(f"Invalid kind value: {kind_value}")
        return cls(kind=kind, url=data.get("url"))

    def to_dict(self) -> dict[str, int | str | None]:
        return {
            "kind": self.kind.value,  # convert Enum to int
            "url": self.url,
        }
