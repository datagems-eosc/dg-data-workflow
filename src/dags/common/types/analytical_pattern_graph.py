from common.types.analytical_pattern_edge import AnalyticalPatternEdge
from common.types.analytical_pattern_node import AnalyticalPatternNode


class AnalyticalPatternGraph:
    def __init__(self, nodes: list[AnalyticalPatternNode], edges: list[AnalyticalPatternEdge]):
        self.nodes = nodes
        self.edges = edges

    def to_dict(self):
        return {
            "nodes": [n.to_dict() for n in self.nodes],
            "edges": [e.to_dict() for e in self.edges]
        }
