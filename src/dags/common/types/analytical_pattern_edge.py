from uuid import UUID

from common.types.analytical_pattern_node import AnalyticalPatternNode


class AnalyticalPatternEdge:
    def __init__(self, frm: UUID, labels: list[str], to: UUID):
        self.frm = frm
        self.labels = labels
        self.to = to

    @classmethod
    def from_nodes(cls, frm: AnalyticalPatternNode, labels: list[str], to: AnalyticalPatternNode):
        return cls(frm=frm.id, labels=labels, to=to.id)

    def to_dict(self):
        return {
            "from": str(self.frm),
            "labels": self.labels,
            "to": str(self.to)
        }
