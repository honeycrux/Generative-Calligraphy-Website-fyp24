from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID

from domain.entity.job import Job
from domain.value.job_input import JobInput


class JobManagementPort(ABC):
    """
    Port for managing jobs.
    """

    @abstractmethod
    def start_job(self, job_input: JobInput) -> UUID:
        """
        Start a job by its ID.

        :param job_input: The input data for the job to start.
        """
        pass

    @abstractmethod
    def retrieve_job(self, job_id: UUID) -> Optional[Job]:
        """
        Retrieve a job by its ID.

        :param job_id: The ID of the job to retrieve.
        :return: The job associated with the job ID.
        """
        pass

    @abstractmethod
    def interrupt_job(self, job_id: UUID) -> None:
        """
        Interrupt a job by its ID.
        Does not raise an error if the job does not exist.

        :param job_id: The ID of the job to interrupt.
        """
        pass
