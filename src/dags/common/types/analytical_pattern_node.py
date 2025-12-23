from dataclasses import dataclass, field
from typing import Any
from uuid import UUID
import uuid


@dataclass
class AnalyticalPatternNode:
    labels: list[str]
    properties: dict[str, Any]
    excluded_properties: list[str]
    id: UUID = field(default_factory=uuid.uuid4)

    def to_dict(self):
        val = {
            "id": str(self.id),
            "labels": self.labels,
            "properties": self.properties
        }
        # if val["properties"].get("type"):
        #     val["properties"]["@type"] = val["properties"]["type"]
        #     val["properties"].pop("type")
        # for prop in self.excluded_properties:
        #     val["properties"].pop(prop, None)
        return val
