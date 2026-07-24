from enum import Enum


class WorkflowProcessStepExecutionStatus(Enum):
    InProgress = 0
    Failed = 1
    Succeeded = 2