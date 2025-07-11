import copy
from typing import Optional
from uuid import UUID

from domain.value.generation_result import GenerationResult, WordResult
from domain.value.job_info import (
    CancelledJob,
    CompletedJob,
    FailedJob,
    JobInfo,
    RunningJob,
    WaitingJob,
)
from domain.value.job_input import JobInput
from domain.value.job_status import JobStatus


class Job:
    __job_id: UUID
    __job_input: JobInput
    __job_status: JobStatus
    __job_info: JobInfo
    __generation_result: GenerationResult

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
        self.__generation_result = GenerationResult.new()

    def update(
        self,
        job_status: JobStatus,
        job_info: JobInfo,
    ) -> None:
        Job.validate_status_info(job_status=job_status, job_info=job_info)
        self.__job_status = job_status
        self.__job_info = job_info

    def add_word_result(self, word: str, image_id: Optional[UUID]) -> None:
        self.__generation_result.add_word_result(WordResult(word, image_id))

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
    def generation_result(self) -> GenerationResult:
        # Create a deep copy to prevent external modification
        return copy.deepcopy(self.__generation_result)

    @staticmethod
    def validate_status_info(
        job_status: JobStatus,
        job_info: JobInfo,
    ) -> None:
        if job_status == JobStatus.WAITING and not isinstance(job_info, WaitingJob):
            raise ValueError("Job status is WAITING but job info is not a WaitingJob.")
        if job_status == JobStatus.RUNNING and not isinstance(job_info, RunningJob):
            raise ValueError("Job status is RUNNING but job info is not a RunningJob.")
        if job_status == JobStatus.COMPLETED and not isinstance(job_info, CompletedJob):
            raise ValueError(
                "Job status is COMPLETED but job info is not a CompletedJob."
            )
        if job_status == JobStatus.FAILED and not isinstance(job_info, FailedJob):
            raise ValueError("Job status is FAILED but job info is not a FailedJob.")
        if job_status == JobStatus.CANCELLED and not isinstance(job_info, CancelledJob):
            raise ValueError(
                "Job status is CANCELLED but job info is not a CancelledJob."
            )
