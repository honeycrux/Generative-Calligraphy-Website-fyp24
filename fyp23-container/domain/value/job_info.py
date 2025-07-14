from abc import ABC
from datetime import datetime
from typing import Optional, Union
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .running_state import RunningState

""" Inheritance structure

[Decision Record](decision-record/use-subclassing-or-union.md)
Subclassing is used for job info types.

JobInfo (BaseModel, ABC)
├── WaitingJob (JobInfo)
├── RunningJob (JobInfo)
└── StoppedJob (JobInfo, ABC)
    ├── CompletedJob (StoppedJob)
    ├── FailedJob (StoppedJob)
    └── CancelledJob (StoppedJob)
"""


class JobInfo(BaseModel, ABC):
    model_config = ConfigDict(frozen=True, extra="forbid")

    time_start_to_queue: datetime


class WaitingJob(JobInfo):
    model_config = ConfigDict(frozen=True, extra="forbid")

    place_in_queue: int

    @staticmethod
    def create(place_in_queue: int) -> "WaitingJob":
        return WaitingJob(
            time_start_to_queue=datetime.now(),
            place_in_queue=place_in_queue,
        )

    def move_up_queue(self) -> "WaitingJob":
        return WaitingJob(
            time_start_to_queue=self.time_start_to_queue,
            place_in_queue=self.place_in_queue - 1,
        )


class RunningJob(JobInfo):
    model_config = ConfigDict(frozen=True, extra="forbid")

    time_start_to_run: datetime
    running_state: RunningState

    @staticmethod
    def of(waiting_job: WaitingJob) -> "RunningJob":
        return RunningJob(
            time_start_to_queue=waiting_job.time_start_to_queue,
            time_start_to_run=datetime.now(),
            running_state=RunningState.not_started(),
        )

    def of_state(self, running_state: RunningState) -> "RunningJob":
        return RunningJob(
            time_start_to_queue=self.time_start_to_queue,
            time_start_to_run=self.time_start_to_run,
            running_state=running_state,
        )


class StoppedJob(JobInfo, ABC):
    model_config = ConfigDict(frozen=True, extra="forbid")

    time_end: datetime


class CompletedJob(StoppedJob):
    model_config = ConfigDict(frozen=True, extra="forbid")

    time_start_to_run: datetime

    @staticmethod
    def of(running_job: RunningJob) -> "CompletedJob":
        return CompletedJob(
            time_start_to_queue=running_job.time_start_to_queue,
            time_start_to_run=running_job.time_start_to_run,
            time_end=datetime.now(),
        )


class FailedJob(StoppedJob):
    model_config = ConfigDict(frozen=True, extra="forbid")

    time_start_to_run: datetime
    error_message: str

    @staticmethod
    def of(running_job: RunningJob, error_message: str) -> "FailedJob":
        return FailedJob(
            time_start_to_queue=running_job.time_start_to_queue,
            time_start_to_run=running_job.time_start_to_run,
            time_end=datetime.now(),
            error_message=error_message,
        )


class CancelledJob(StoppedJob):
    model_config = ConfigDict(frozen=True, extra="forbid")

    time_start_to_run: Optional[datetime]

    @staticmethod
    def of(job: Union[WaitingJob, RunningJob]) -> "CancelledJob":
        return CancelledJob(
            time_start_to_queue=job.time_start_to_queue,
            time_start_to_run=(
                job.time_start_to_run if isinstance(job, RunningJob) else None
            ),
            time_end=datetime.now(),
        )
