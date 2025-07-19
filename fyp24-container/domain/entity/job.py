import copy
from uuid import UUID

from domain.value.generated_word_location import GeneratedWordLocation
from domain.value.job_info import (
    CancelledJob,
    CompletedJob,
    FailedJob,
    JobInfo,
    RunningJob,
    WaitingJob,
)
from domain.value.job_input import JobInput
from domain.value.job_result import JobResult
from domain.value.job_status import JobStatus


class Job:
    __job_id: UUID
    __job_input: JobInput
    __job_status: JobStatus
    __job_info: JobInfo
    __job_result: JobResult

    def __init__(
        self,
        job_id: UUID,
        job_input: JobInput,
        job_status: JobStatus,
        job_info: JobInfo,
    ):
        Job.validate_status_info(job_status=job_status, job_info=job_info)
        self.__job_id = job_id
        self.__job_input = job_input
        self.__job_status = job_status
        self.__job_info = job_info
        self.__job_result = JobResult.new()

    def update(
        self,
        job_status: JobStatus,
        job_info: JobInfo,
    ) -> None:
        Job.validate_status_info(job_status=job_status, job_info=job_info)
        self.__job_status = job_status
        self.__job_info = job_info

    def add_generated_word_location(
        self, generated_word_location: GeneratedWordLocation
    ) -> None:
        self.__job_result.add_word_location(generated_word_location)

    @property
    def job_id(self) -> UUID:
        # Create a deep copy to prevent external modification
        return copy.deepcopy(self.__job_id)

    @property
    def job_input(self) -> JobInput:
        # Create a deep copy to prevent external modification
        return copy.deepcopy(self.__job_input)

    @property
    def job_status(self) -> JobStatus:
        # Create a deep copy to prevent external modification
        return copy.deepcopy(self.__job_status)

    @property
    def job_info(self) -> JobInfo:
        # Create a deep copy to prevent external modification
        return copy.deepcopy(self.__job_info)

    @property
    def job_result(self) -> JobResult:
        # Create a deep copy to prevent external modification
        return copy.deepcopy(self.__job_result)

    @staticmethod
    def validate_status_info(
        job_status: JobStatus,
        job_info: JobInfo,
    ) -> None:
        if job_status == JobStatus.Waiting and not isinstance(job_info, WaitingJob):
            raise ValueError("Job status is waiting but job info is not a WaitingJob.")
        if job_status == JobStatus.Running and not isinstance(job_info, RunningJob):
            raise ValueError("Job status is running but job info is not a RunningJob.")
        if job_status == JobStatus.Completed and not isinstance(job_info, CompletedJob):
            raise ValueError(
                "Job status is completed but job info is not a CompletedJob."
            )
        if job_status == JobStatus.Failed and not isinstance(job_info, FailedJob):
            raise ValueError("Job status is failed but job info is not a FailedJob.")
        if job_status == JobStatus.Cancelled and not isinstance(job_info, CancelledJob):
            raise ValueError(
                "Job status is cancelled but job info is not a CancelledJob."
            )
