from dataclasses import dataclass
from uuid import UUID

from common.types.analytical_pattern_node import AnalyticalPatternNode


@dataclass
class AnalyticalPatternEdge:
    frm: UUID
    labels: list[str]
    to: UUID

    @classmethod
    def from_nodes(cls, frm: AnalyticalPatternNode, labels: list[str], to: AnalyticalPatternNode):
        return cls(frm=frm.id, labels=labels, to=to.id)

    def to_dict(self):
        return {
            "from": str(self.frm),
            "labels": self.labels,
            "to": str(self.to)
        }
