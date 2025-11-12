from typing import Any
from uuid import UUID, uuid4


class AnalyticalPatternNode:
    def __init__(self, labels: list[str], properties: dict[str, Any]):
        self.id: UUID = uuid4()
        self.labels = labels
        self.properties = properties

    def to_dict(self):
        return {
            "@id": str(self.id),
            "labels": self.labels,
            "properties": self.properties
        }
