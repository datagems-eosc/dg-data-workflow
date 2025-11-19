from dataclasses import dataclass
from typing import Any
from uuid import UUID, uuid4


@dataclass
class AnalyticalPatternNode:
    labels: list[str]
    properties: dict[str, Any]
    id: UUID = uuid4()

    def to_dict(self):
        return {
            "@id": str(self.id),
            "labels": self.labels,
            "properties": self.properties
        }
