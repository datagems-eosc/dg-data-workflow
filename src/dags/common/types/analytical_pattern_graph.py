from dataclasses import dataclass

from common.types.analytical_pattern_edge import AnalyticalPatternEdge
from common.types.analytical_pattern_node import AnalyticalPatternNode


@dataclass
class AnalyticalPatternGraph:
    nodes: list[AnalyticalPatternNode]
    edges: list[AnalyticalPatternEdge]

    def to_dict(self):
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges]
        }
