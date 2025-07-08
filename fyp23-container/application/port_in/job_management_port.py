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
    def start_task(self, job_input: JobInput) -> UUID:
        """
        Start a task by its ID.

        :param job_input: The input data for the job to start.
        """
        pass

    @abstractmethod
    def retrieve_task(self, task_id: UUID) -> Optional[Job]:
        """
        Retrieve a task by its ID.

        :param task_id: The ID of the task to retrieve.
        :return: The job associated with the task ID.
        """
        pass

    @abstractmethod
    def interrupt_task(self, task_id: UUID) -> None:
        """
        Interrupt a task by its ID.

        :param task_id: The ID of the task to interrupt.
        """
        pass
