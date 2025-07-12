from asyncio import Task
from datetime import datetime, timedelta
from typing import Callable, Optional, Union
from uuid import UUID

from domain.entity.job import Job
from domain.exception.job_table_id_conflict import JobTableIDConflict
from domain.value.job_result import JobResult
from domain.value.job_info import (
    CancelledJob,
    RunningJob,
    StoppedJob,
    WaitingJob,
)
from domain.value.job_status import JobStatus


class JobTable:
    __jobs: dict[UUID, Job]
    __coroutines: dict[UUID, Optional[Task[Union[JobResult, str]]]]

    # Maximum time to retain completed jobs in the table
    __max_retain_time: timedelta

    def __init__(self, max_retain_time: timedelta):
        self.__max_retain_time = max_retain_time
        self.__jobs = {}
        self.__coroutines = {}

    def add_job(self, job: Job) -> None:
        if job.job_id in self.__jobs:
            raise JobTableIDConflict(
                f"Add job of ID {job.job_id} while another job with the same ID already exists."
            )
        self.__jobs[job.job_id] = job

    def get_job(self, job_id: UUID) -> Optional[Job]:
        if job_id not in self.__jobs:
            return None
        return self.__jobs[job_id]

    def cancel_job(self, task_id: UUID) -> None:
        job = self.get_job(task_id)
        if job is None:
            # Task not found, nothing to interrupt
            return
        if not (
            isinstance(job.job_info, WaitingJob) or isinstance(job.job_info, RunningJob)
        ):
            # Task is not in a state that can be interrupted
            return

        coroutine = self.__get_coroutine(task_id)
        if coroutine is not None and not coroutine.cancelled():
            # Cancel the executing coroutine if it exists
            coroutine.cancel()

        job.update(
            job_status=JobStatus.CANCELLED,
            job_info=CancelledJob.of(job.job_info),
        )

    def add_coroutine(self, job_id: UUID, coroutine: Task) -> None:
        if job_id not in self.__jobs:
            # Job does not exist, cannot add coroutine
            return
        if job_id in self.__coroutines:
            raise JobTableIDConflict(
                f"Add coroutine for the job {job_id} that already has a coroutine."
            )
        self.__coroutines[job_id] = coroutine

    def cleanup(self, on_delete_resource: Callable[[UUID], None]) -> None:
        current_time = datetime.now()
        to_remove = [
            job_id
            for job_id, job in self.__jobs.items()
            if isinstance(job.job_info, StoppedJob)
            and (current_time - job.job_info.time_end) > self.__max_retain_time
        ]
        for job_id in to_remove:
            # Remove the job and its associated coroutine
            job = self.__jobs.pop(job_id, None)
            self.__coroutines.pop(job_id, None)

            # Clean up resources associated with the job
            if job is not None:
                for word_location in job.job_result.generated_word_locations:
                    if word_location.image_id is not None:
                        on_delete_resource(word_location.image_id)

    def __get_coroutine(self, job_id: UUID) -> Optional[Task]:
        if job_id not in self.__coroutines:
            return None
        return self.__coroutines[job_id]
