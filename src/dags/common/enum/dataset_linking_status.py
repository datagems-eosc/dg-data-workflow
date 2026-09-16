from enum import Enum


class DatasetLinkingStatus(Enum):
    QUEUED = "queued"
    IN_PROGRESS = "in_progress"
    FAILED = "failed"
    COMPLETED = "completed"
