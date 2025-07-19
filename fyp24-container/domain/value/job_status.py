from enum import Enum


class JobStatus(Enum):
    Waiting = "waiting"
    Running = "running"
    Completed = "completed"
    Failed = "failed"
    Cancelled = "cancelled"
