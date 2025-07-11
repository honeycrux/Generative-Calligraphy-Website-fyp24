from abc import ABC
from typing import Optional, Union
from uuid import UUID
from pydantic import BaseModel, ConfigDict
from datetime import datetime

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

    job_id: UUID
    time_start_to_queue: datetime


class WaitingJob(JobInfo):
    model_config = ConfigDict(frozen=True, extra="forbid")

    place_in_queue: int

    @staticmethod
    def create(job_id: UUID, place_in_queue: int) -> "WaitingJob":
        return WaitingJob(
            job_id=job_id,
            time_start_to_queue=datetime.now(),
            place_in_queue=place_in_queue,
        )


class RunningJob(JobInfo):
    model_config = ConfigDict(frozen=True, extra="forbid")

    time_start_to_run: datetime
    running_state: RunningState

    @staticmethod
    def of(waiting_job: WaitingJob) -> "RunningJob":
        return RunningJob(
            job_id=waiting_job.job_id,
            time_start_to_queue=waiting_job.time_start_to_queue,
            time_start_to_run=datetime.now(),
            running_state=RunningState.not_started(),
        )

    def of_state(self, running_state: RunningState) -> "RunningJob":
        return RunningJob(
            job_id=self.job_id,
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
            job_id=running_job.job_id,
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
            job_id=running_job.job_id,
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
            job_id=job.job_id,
            time_start_to_queue=job.time_start_to_queue,
            time_start_to_run=(
                job.time_start_to_run if isinstance(job, RunningJob) else None
            ),
            time_end=datetime.now(),
        )
