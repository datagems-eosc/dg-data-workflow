from enum import Enum


class AnalyticalPatternNodeStatus(Enum):
    STAGED = "staged"
    LOADED = "loaded"
    READY = "ready"
