import time
from uuid import UUID
import pytest

from application.job_management_service import JobManagementService
from application.port_in.job_management_port import JobManagementPort
from application.port_out.font_generation_application_port import (
    FontGenerationApplicationPort,
)
from domain.entity.job import Job
from domain.value.font_gen_service_config import FontGenServiceConfig
from domain.value.job_input import FontGenModel, JobInput
from domain.value.job_status import JobStatus
from tests.font_generation_application_mock import FontGenerationApplicationMock


### Constants ###


TASK_PROCESSING_TIME = 0.1  # seconds
OPERATE_QUEUE_INTERVAL = 0.01  # seconds
MAX_RETAIN_TIME = 0.3  # seconds
TINY_BUFFER = (
    0.02  # seconds; we find 0.01 too short for some systems to process the task
)


### Fixtures ###


@pytest.fixture
def job_management_service() -> JobManagementService:
    config = FontGenServiceConfig(
        operate_queue_interval=OPERATE_QUEUE_INTERVAL,
        max_retain_time=MAX_RETAIN_TIME,
    )
    font_app: FontGenerationApplicationPort = FontGenerationApplicationMock(
        run_seconds=TASK_PROCESSING_TIME,
        simulate_success=True,
    )
    return JobManagementService(
        font_generation_application_port=font_app,
        font_gen_service_config=config,
    )


@pytest.fixture
def job_management_service_that_fails() -> JobManagementService:
    config = FontGenServiceConfig(
        operate_queue_interval=OPERATE_QUEUE_INTERVAL,
        max_retain_time=MAX_RETAIN_TIME,
    )
    font_app: FontGenerationApplicationPort = FontGenerationApplicationMock(
        run_seconds=TASK_PROCESSING_TIME,
        simulate_success=False,
    )
    return JobManagementService(
        font_generation_application_port=font_app,
        font_gen_service_config=config,
    )


@pytest.fixture
def job_management_port(job_management_service) -> JobManagementPort:
    return job_management_service


@pytest.fixture
def job_management_port_that_fails(
    job_management_service_that_fails,
) -> JobManagementPort:
    return job_management_service_that_fails


### Helper Functions ###


def add_task(job_management_port: JobManagementPort) -> UUID:
    job_input = JobInput(model_id=FontGenModel.fyp23, input_text="")
    job_id = job_management_port.start_task(job_input)
    assert job_id is not None, "Job ID should not be None after starting a task"
    return job_id


def retrieve_existing_task(job_management_port: JobManagementPort, job_id: UUID) -> Job:
    job = job_management_port.retrieve_task(job_id)
    assert job is not None, "Job should be retrievable"
    return job


def cancel_task(job_management_port: JobManagementPort, job_id: UUID) -> None:
    job_management_port.interrupt_task(job_id)


### Tests ###


def test_can_add_one_task(job_management_port):
    add_task(job_management_port)


def test_can_add_multiple_task(job_management_port):
    job_id_1 = add_task(job_management_port)
    job_id_2 = add_task(job_management_port)
    assert job_id_1 != job_id_2, "Job IDs should be unique for different tasks"


def test_cannot_retrieve_non_existent_task(job_management_port):
    non_existent_id = "12345678-1234-5678-1234-567812345678"
    job = job_management_port.retrieve_task(non_existent_id)
    assert job is None, "Retrieving a non-existent task should return None"


def test_added_task_is_put_to_waiting(job_management_port):
    job_id = add_task(job_management_port)

    job = retrieve_existing_task(job_management_port, job_id)
    assert (
        job.job_status == JobStatus.WAITING
    ), "Job status should be WAITING after being added"


def test_added_task_can_start(job_management_port):
    job_id = add_task(job_management_port)

    time.sleep(0.05)  # Wait for the task to be started

    job = retrieve_existing_task(job_management_port, job_id)
    assert (
        job.job_status == JobStatus.RUNNING
    ), "Job status should be RUNNING after starting"


def test_started_task_can_complete(job_management_port):
    job_id = add_task(job_management_port)

    time.sleep(
        TASK_PROCESSING_TIME + OPERATE_QUEUE_INTERVAL + TINY_BUFFER
    )  # Wait for the task to be processed

    job = retrieve_existing_task(job_management_port, job_id)
    assert (
        job.job_status == JobStatus.COMPLETED
    ), "Job status should be COMPLETED after processing"


def test_started_task_can_fail(job_management_port_that_fails):
    job_id = add_task(job_management_port_that_fails)

    time.sleep(
        TASK_PROCESSING_TIME + OPERATE_QUEUE_INTERVAL + TINY_BUFFER
    )  # Wait for the task to be processed

    job = retrieve_existing_task(job_management_port_that_fails, job_id)
    assert (
        job.job_status == JobStatus.FAILED
    ), "Job status should be FAILED after processing with failure simulation"


def test_can_cancel_waiting_task(job_management_port):
    job_id = add_task(job_management_port)

    job = retrieve_existing_task(job_management_port, job_id)
    assert (
        job.job_status == JobStatus.WAITING
    ), "Job status should be WAITING before cancellation"

    cancel_task(job_management_port, job_id)

    job = retrieve_existing_task(job_management_port, job_id)
    assert (
        job.job_status == JobStatus.CANCELLED
    ), "Job status should be CANCELLED after being interrupted"

    time.sleep(
        TASK_PROCESSING_TIME + OPERATE_QUEUE_INTERVAL + TINY_BUFFER
    )  # Wait for the task to be processed as if it was not cancelled
    job = retrieve_existing_task(job_management_port, job_id)
    assert (
        job.job_status == JobStatus.CANCELLED
    ), "Job status should remain CANCELLED after processing attempt post-cancellation"


def test_can_cancel_running_task(job_management_port):
    job_id = add_task(job_management_port)

    time.sleep(0.05)  # Wait for the task to be in RUNNING state

    job = retrieve_existing_task(job_management_port, job_id)
    assert (
        job.job_status == JobStatus.RUNNING
    ), "Job status should be RUNNING before cancellation"

    cancel_task(job_management_port, job_id)

    job = retrieve_existing_task(job_management_port, job_id)
    assert (
        job.job_status == JobStatus.CANCELLED
    ), "Job status should be CANCELLED after being interrupted"

    time.sleep(
        TASK_PROCESSING_TIME + OPERATE_QUEUE_INTERVAL + TINY_BUFFER
    )  # Wait for the task to be processed as if it was not cancelled
    job = retrieve_existing_task(job_management_port, job_id)
    assert (
        job.job_status == JobStatus.CANCELLED
    ), "Job status should remain CANCELLED after processing attempt post-cancellation"


def test_cannot_cancel_completed_task(job_management_port):
    job_id = add_task(job_management_port)

    time.sleep(
        TASK_PROCESSING_TIME + OPERATE_QUEUE_INTERVAL + TINY_BUFFER
    )  # Wait for the task to be processed

    job = retrieve_existing_task(job_management_port, job_id)
    assert (
        job.job_status == JobStatus.COMPLETED
    ), "Job status should be COMPLETED before cancellation"

    cancel_task(job_management_port, job_id)

    job = retrieve_existing_task(job_management_port, job_id)
    assert (
        job.job_status == JobStatus.COMPLETED
    ), "Job status should remain COMPLETED after attempting to cancel a completed task"


def test_cannot_cancel_failed_task(job_management_port_that_fails):
    job_id = add_task(job_management_port_that_fails)

    time.sleep(
        TASK_PROCESSING_TIME + OPERATE_QUEUE_INTERVAL + TINY_BUFFER
    )  # Wait for the task to be processed

    job = retrieve_existing_task(job_management_port_that_fails, job_id)
    assert (
        job.job_status == JobStatus.FAILED
    ), "Job status should be FAILED before cancellation"

    cancel_task(job_management_port_that_fails, job_id)

    job = retrieve_existing_task(job_management_port_that_fails, job_id)
    assert (
        job.job_status == JobStatus.FAILED
    ), "Job status should remain FAILED after attempting to cancel a failed task"


def test_process_job_in_input_order(job_management_port):
    job_id_1 = add_task(job_management_port)
    job_id_2 = add_task(job_management_port)

    # Wait for the first job to complete
    time.sleep(TASK_PROCESSING_TIME + OPERATE_QUEUE_INTERVAL + TINY_BUFFER)
    job_1 = retrieve_existing_task(job_management_port, job_id_1)
    assert (
        job_1.job_status == JobStatus.COMPLETED
    ), "First job should run first and completed"
    job_2 = retrieve_existing_task(job_management_port, job_id_2)
    assert (
        job_2.job_status == JobStatus.RUNNING
    ), "Second job should be in RUNNING status after first job completion"

    # Wait for the second job to complete
    time.sleep(TASK_PROCESSING_TIME)
    job_2 = retrieve_existing_task(job_management_port, job_id_2)
    assert (
        job_2.job_status == JobStatus.COMPLETED
    ), "Second job status should be COMPLETED after processing"


def test_can_retrieve_task_at_or_before_retain_time(job_management_port):
    job_id = add_task(job_management_port)

    time.sleep(TASK_PROCESSING_TIME)  # Wait for the task to be processed

    # Wait for some time less than MAX_RETAIN_TIME
    time.sleep(MAX_RETAIN_TIME - TINY_BUFFER)

    # Try to retrieve the task again
    job = job_management_port.retrieve_task(job_id)
    assert job is not None, "Job should still be retrievable within retain time"


def test_no_guarantee_of_retrieving_task_between_once_and_twice_the_retain_time(
    job_management_port,
):
    job_id = add_task(job_management_port)

    time.sleep(TASK_PROCESSING_TIME)  # Wait for the task to be processed

    # Wait between once and twice the MAX_RETAIN_TIME
    time.sleep(MAX_RETAIN_TIME + TINY_BUFFER)

    # Try to retrieve the task again
    job = job_management_port.retrieve_task(job_id)
    assert (
        job is not None or job is None
    ), "Job may or may not be retrievable after once the retain time has passed"


def test_cannot_retrieve_task_after_twice_the_retain_time(job_management_port):
    job_id = add_task(job_management_port)

    time.sleep(
        TASK_PROCESSING_TIME + OPERATE_QUEUE_INTERVAL + TINY_BUFFER
    )  # Wait for the task to be processed

    # Wait for more than twice the MAX_RETAIN_TIME
    time.sleep(MAX_RETAIN_TIME * 2 + TINY_BUFFER)

    # Try to retrieve the task again
    job = job_management_port.retrieve_task(job_id)
    assert job is None, "Job should not be retrievable after retain time"
