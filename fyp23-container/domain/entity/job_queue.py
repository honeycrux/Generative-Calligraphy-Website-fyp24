from queue import Queue
from typing import Callable
from uuid import UUID

from domain.exception.retrieval_from_empty_job_queue import RetrievalFromEmptyJobQueue


class JobQueue:
    __job_queue: Queue[UUID]

    def __init__(self):
        self.__job_queue = Queue()

    def add_job(self, job_id: UUID) -> None:
        if job_id in self.__job_queue.queue:
            # Job is already in the queue, no need to add it again
            return
        self.__job_queue.put(job_id)

    def dequeue_job(self, shift_queue: Callable[[], None]) -> UUID:
        if self.__job_queue.empty():
            raise RetrievalFromEmptyJobQueue("Dequeue a job from an empty queue.")
        shift_queue()
        return self.__job_queue.get()

    def is_empty(self) -> bool:
        return self.__job_queue.empty()

    def size(self) -> int:
        return self.__job_queue.qsize()
