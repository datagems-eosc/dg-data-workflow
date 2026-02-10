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
        props = dict(self.properties)
        for prop in self.excluded_properties:
            props.pop(prop, None)
        return {
            "id": str(self.id),
            "labels": self.labels,
            "properties": props,
        }
