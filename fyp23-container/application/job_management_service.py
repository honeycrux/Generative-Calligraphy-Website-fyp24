import asyncio
from datetime import timedelta
import threading
import time
from typing import Optional
from uuid import UUID, uuid4

from application.port_in.job_management_port import JobManagementPort
from application.port_out.font_generation_application_port import (
    FontGenerationApplicationPort,
)
from application.port_out.image_repository_port import ImageRepositoryPort
from domain.entity.job import Job
from domain.entity.job_queue import JobQueue
from domain.entity.job_table import JobTable
from domain.value.font_gen_service_config import FontGenServiceConfig
from domain.value.image_data import ImageData
from domain.value.job_info import (
    CancelledJob,
    CompletedJob,
    FailedJob,
    RunningJob,
    WaitingJob,
)
from domain.value.job_input import JobInput
from domain.value.job_status import JobStatus
from domain.value.running_state import RunningState


class JobManagementService(JobManagementPort):
    __config: FontGenServiceConfig
    __job_table: JobTable
    __job_queue: JobQueue
    __font_generation_application_port: FontGenerationApplicationPort
    __image_repository_port: ImageRepositoryPort
    __operate_queue_thread: threading.Thread
    __cleanup_job_table_thread: threading.Thread

    def __init__(
        self,
        font_generation_application_port: FontGenerationApplicationPort,
        font_gen_service_config: FontGenServiceConfig,
        image_repository_port: ImageRepositoryPort,
    ):
        self.__config = font_gen_service_config
        self.__font_generation_application_port = font_generation_application_port
        self.__image_repository_port = image_repository_port

        max_retain_time = timedelta(seconds=font_gen_service_config.max_retain_time)
        self.__job_table = JobTable(max_retain_time=max_retain_time)
        self.__job_queue = JobQueue()

        self.__operate_queue_thread = self.continuously_operate_queue()
        self.__cleanup_job_table_thread = self.continuously_cleanup_job_table()

    def start_task(self, job_input: JobInput):
        new_job_id = uuid4()
        queue_size = self.__job_queue.size()
        new_job = Job(
            job_id=new_job_id,
            job_input=job_input,
            job_status=JobStatus.WAITING,
            job_info=WaitingJob.create(job_id=new_job_id, place_in_queue=queue_size),
        )
        self.__job_table.add_job(new_job)
        self.__job_queue.add_job(new_job_id)
        return new_job_id

    def retrieve_task(self, task_id: UUID) -> Optional[Job]:
        return self.__job_table.get_job(task_id)

    def interrupt_task(self, task_id: UUID) -> None:
        self.__job_table.cancel_job(task_id)

    def continuously_operate_queue(self) -> threading.Thread:
        def on_new_state(job: Job, state: RunningState):
            assert isinstance(
                job.job_info, RunningJob
            ), "Job info should be RunningJob at this point"

            # Update job info with the new state
            job.update(
                job_status=JobStatus.RUNNING,
                job_info=job.job_info.of_state(state),
            )

        def on_new_word_result(job: Job, word: str, image_data: Optional[ImageData]):
            image_id = image_data.image_id if image_data else None
            success = image_data is not None

            # Add the word result to the job's generation result
            job.add_word_result(word=word, success=success, image_id=image_id)

            if success and image_data is not None:
                # If the image data is available, save it to the file system
                self.__image_repository_port.save_image(image_data=image_data)

        async def operate_queue() -> None:
            if self.__job_queue.size() < 1:
                # No jobs in the queue, wait for a while before checking again
                if self.__config.operate_queue_interval > 0:
                    await asyncio.sleep(self.__config.operate_queue_interval)
                return

            job_id = self.__job_queue.dequeue_job()
            job = self.__job_table.get_job(job_id)

            if job is None:
                # Job not found in the table, nothing to process
                return

            if not isinstance(job.job_info, WaitingJob):
                # Job is not in a waiting state, nothing to process
                return

            # Update job status and info
            job.update(
                job_status=JobStatus.RUNNING,
                job_info=RunningJob.of(job.job_info),
            )

            assert isinstance(
                job.job_info, RunningJob
            ), "Job info should be RunningJob at this point"

            # Start the font generation task
            task_coroutine = self.__font_generation_application_port.generate_text(
                job_input=job.job_input,
                job_info=job.job_info,
                on_new_state=lambda state: on_new_state(job, state),
                on_new_word_result=lambda word, image_data: on_new_word_result(
                    job=job, word=word, image_data=image_data
                ),
            )

            # Add the coroutine to the job table
            self.__job_table.add_coroutine(job_id, task_coroutine)

            # Wait for the task to complete and handle the result
            try:
                result = await task_coroutine

                if isinstance(result, bool):
                    if result:
                        # Task was successful
                        job.update(
                            job_status=JobStatus.COMPLETED,
                            job_info=CompletedJob.of(job.job_info),
                        )
                    else:
                        raise ValueError(
                            "Task returned False, but no error message was provided."
                        )

                if isinstance(result, str):
                    # Task failed with an error message
                    job.update(
                        job_status=JobStatus.FAILED,
                        job_info=FailedJob.of(job.job_info, error_message=result),
                    )
                    return

            except asyncio.CancelledError:
                # Task was cancelled
                job.update(
                    job_status=JobStatus.CANCELLED,
                    job_info=CancelledJob.of(job.job_info),
                )
                return

            except Exception as e:
                # An unexpected error occurred
                job.update(
                    job_status=JobStatus.FAILED,
                    job_info=FailedJob.of(job.job_info, error_message=str(e)),
                )
                return

        async def always_operate_queue() -> None:
            while True:
                try:
                    await operate_queue()
                except asyncio.CancelledError:
                    # If the task is cancelled, exit the loop
                    break

        # Continuously run the above process
        operate_queue_thread = threading.Thread(
            target=lambda: asyncio.run(always_operate_queue()),
            args=(),
            # Ensure the thread is a daemon thread so it doesn't block program exit
            daemon=True,
        )
        operate_queue_thread.start()

        return operate_queue_thread

    def continuously_cleanup_job_table(self) -> threading.Thread:
        def on_delete_resource(image_id: UUID) -> None:
            # Delete the image resource from the repository
            self.__image_repository_port.delete_image(image_id=image_id)

        def cleanup_job_table() -> None:
            # Clean up job table
            self.__job_table.cleanup(on_delete_resource=on_delete_resource)

            # Wait for the configured max retain time before the next cleanup
            time.sleep(self.__config.max_retain_time)

        def always_cleanup_job_table() -> None:
            while True:
                cleanup_job_table()

        # Continuously run the above process
        continuously_cleanup_job_table_thread = threading.Thread(
            target=always_cleanup_job_table,
            args=(),
            # Ensure the thread is a daemon thread so it doesn't block program exit
            daemon=True,
        )
        continuously_cleanup_job_table_thread.start()

        return continuously_cleanup_job_table_thread
