import time
from uuid import UUID

import pytest

from application.image_access_service import ImageAccessService
from application.job_management_service import JobManagementService
from application.port_in.image_accessor_port import ImageAccessorPort
from application.port_in.job_management_port import JobManagementPort
from application.port_out.image_repository_port import ImageRepositoryPort
from application.port_out.text_generator_port import TextGeneratorPort
from domain.entity.job import Job
from domain.value.font_gen_service_config import FontGenServiceConfig
from domain.value.job_info import FailedJob, RunningJob, WaitingJob
from domain.value.job_input import JobInput
from domain.value.job_status import JobStatus
from tests.application.image_repository_stub import ImageRepositoryStub
from tests.application.text_generator_stub import TextGeneratorStub
from tests.application.text_generator_with_progress_stub import (
    TextGeneratorWithProgressStub,
)

### Constants ###


JOB_PROCESSING_TIME = 0.1  # seconds
OPERATE_QUEUE_INTERVAL = 0.01  # seconds
MAX_RETAIN_TIME = 0.3  # seconds
TINY_BUFFER = 0.04  # seconds; we found that 0.03 sometimes fails due to timing issues
PROGRESS_INTERVAL = 0.1  # seconds


### Fixtures ###


@pytest.fixture
def image_repository_port() -> ImageRepositoryPort:
    return ImageRepositoryStub()


@pytest.fixture
def image_accessor_port(image_repository_port) -> ImageAccessorPort:
    return ImageAccessService(image_repository_port=image_repository_port)


@pytest.fixture
def job_management_service(image_repository_port) -> JobManagementService:
    config = FontGenServiceConfig(
        operate_queue_interval=OPERATE_QUEUE_INTERVAL,
        max_retain_time=MAX_RETAIN_TIME,
    )
    font_application: TextGeneratorPort = TextGeneratorStub(
        job_processing_time=JOB_PROCESSING_TIME,
        simulate_success=True,
    )
    return JobManagementService(
        text_generator_port=font_application,
        image_repository_port=image_repository_port,
        font_gen_service_config=config,
    )


@pytest.fixture
def job_management_service_that_fails(image_repository_port) -> JobManagementService:
    config = FontGenServiceConfig(
        operate_queue_interval=OPERATE_QUEUE_INTERVAL,
        max_retain_time=MAX_RETAIN_TIME,
    )
    font_application: TextGeneratorPort = TextGeneratorStub(
        job_processing_time=JOB_PROCESSING_TIME,
        simulate_success=False,
    )
    return JobManagementService(
        text_generator_port=font_application,
        font_gen_service_config=config,
        image_repository_port=image_repository_port,
    )


@pytest.fixture
def job_management_service_with_progress(image_repository_port) -> JobManagementService:
    config = FontGenServiceConfig(
        operate_queue_interval=OPERATE_QUEUE_INTERVAL,
        max_retain_time=MAX_RETAIN_TIME,
    )
    font_application: TextGeneratorPort = TextGeneratorWithProgressStub(
        progress_interval=PROGRESS_INTERVAL
    )
    return JobManagementService(
        text_generator_port=font_application,
        font_gen_service_config=config,
        image_repository_port=image_repository_port,
    )


@pytest.fixture
def job_management_port(job_management_service) -> JobManagementPort:
    return job_management_service


@pytest.fixture
def job_management_port_that_fails(
    job_management_service_that_fails,
) -> JobManagementPort:
    return job_management_service_that_fails


@pytest.fixture
def job_management_port_with_progress(
    job_management_service_with_progress,
) -> JobManagementPort:
    return job_management_service_with_progress


### Helper Functions ###


def add_job(job_management_port: JobManagementPort) -> UUID:
    job_input = JobInput(input_text="中文字")
    job_id = job_management_port.start_job(job_input)
    assert job_id is not None, "Job ID should not be None after starting a job"
    return job_id


def retrieve_existing_job(job_management_port: JobManagementPort, job_id: UUID) -> Job:
    job = job_management_port.retrieve_job(job_id)
    assert job is not None, "Job should be retrievable"
    return job


def cancel_job(job_management_port: JobManagementPort, job_id: UUID) -> None:
    job_management_port.interrupt_job(job_id)


def add_and_complete_job(job_management_port) -> tuple[UUID, Job]:
    job_id = add_job(job_management_port)

    time.sleep(
        JOB_PROCESSING_TIME + OPERATE_QUEUE_INTERVAL + TINY_BUFFER
    )  # Wait for the job to be processed

    job = retrieve_existing_job(job_management_port, job_id)

    if isinstance(job.job_info, FailedJob):
        raise Exception(job.job_info.error_message)

    assert (
        job.job_status == JobStatus.Completed
    ), "Job status should be completed after processing"

    return job_id, job


### Tests ###


def test_can_add_one_job(job_management_port):
    add_job(job_management_port)


def test_can_add_multiple_job(job_management_port):
    job_id_1 = add_job(job_management_port)
    job_id_2 = add_job(job_management_port)
    assert job_id_1 != job_id_2, "Job IDs should be unique for different jobs"


def test_cannot_retrieve_non_existent_job(job_management_port):
    non_existent_id = "12345678-1234-5678-1234-567812345678"
    job = job_management_port.retrieve_job(non_existent_id)
    assert job is None, "Retrieving a non-existent job should return None"


def test_added_job_is_put_to_waiting(job_management_port):
    job_id = add_job(job_management_port)

    job = retrieve_existing_job(job_management_port, job_id)
    assert (
        job.job_status == JobStatus.Waiting
    ), "Job status should be waiting after being added"
    assert isinstance(job.job_info, WaitingJob), "Job info should be of type WaitingJob"
    assert job.job_info.place_in_queue == 1, "Job should be first in the queue"


def test_added_job_can_run_with_resources_available(job_management_port):
    job_id = add_job(job_management_port)

    # Wait for the job to be started
    time.sleep(JOB_PROCESSING_TIME / 2)

    job = retrieve_existing_job(job_management_port, job_id)
    assert (
        job.job_status == JobStatus.Running
    ), "Job status should be running after starting"
    assert (
        job.job_result is not None
    ), "Job resources should be available when the job is running"


def test_running_state_updates_correctly(job_management_port_with_progress):
    job_id = add_job(job_management_port_with_progress)

    # Allow some time for the job to start
    time.sleep(JOB_PROCESSING_TIME / 2)

    job = retrieve_existing_job(job_management_port_with_progress, job_id)
    assert (
        job.job_status == JobStatus.Running
    ), "Job status should be running after starting"
    assert isinstance(job.job_info, RunningJob), "Job info should be of type RunningJob"
    assert (
        job.job_info.running_state.name == "generating"
    ), "Running state should be generating after starting the job"
    assert (
        job.job_info.running_state.message == "Generating: 0/3"
    ), "Running state message should indicate the current progress (0/3 characters)"

    # Wait for one character to be generated
    time.sleep(JOB_PROCESSING_TIME)

    job = retrieve_existing_job(job_management_port_with_progress, job_id)
    assert isinstance(job.job_info, RunningJob), "Job info should be of type RunningJob"
    assert (
        job.job_info.running_state.message == "Generating: 1/3"
    ), "Running state message should indicate the current progress (1/3 characters)"

    # Wait for one character to be generated
    time.sleep(JOB_PROCESSING_TIME)

    job = retrieve_existing_job(job_management_port_with_progress, job_id)
    assert isinstance(job.job_info, RunningJob), "Job info should be of type RunningJob"
    assert (
        job.job_info.running_state.message == "Generating: 2/3"
    ), "Running state message should indicate the current progress (2/3 characters)"


def test_started_job_can_complete_with_results_for_all_input_words(
    job_management_port,
):
    job_id, job = add_and_complete_job(job_management_port)

    # Check if images are saved
    assert len(job.job_result.generated_word_locations) == len(
        job.job_input.input_text
    ), "Number of word results should match the input text length"


def test_images_can_be_retrieved(job_management_port, image_accessor_port):
    job_id, job = add_and_complete_job(job_management_port)

    # Check if successful images can be retrieved
    for word_location in job.job_result.generated_word_locations:
        if word_location.image_id is not None:
            image = image_accessor_port.get_image(word_location.image_id)
            assert (
                image is not None
            ), f"Image data should not be None for word '{word_location.word}'"


def test_started_job_can_fail(job_management_port_that_fails):
    job_id = add_job(job_management_port_that_fails)

    # Wait for the job to be processed
    time.sleep(JOB_PROCESSING_TIME + OPERATE_QUEUE_INTERVAL + TINY_BUFFER)

    job = retrieve_existing_job(job_management_port_that_fails, job_id)
    assert (
        job.job_status == JobStatus.Failed
    ), "Job status should be failed after processing with failure simulation"


def test_can_cancel_waiting_job(job_management_port):
    job_id = add_job(job_management_port)

    job = retrieve_existing_job(job_management_port, job_id)
    assert (
        job.job_status == JobStatus.Waiting
    ), "Job status should be waiting before cancellation"

    cancel_job(job_management_port, job_id)

    job = retrieve_existing_job(job_management_port, job_id)
    assert (
        job.job_status == JobStatus.Cancelled
    ), "Job status should be cancelled after being interrupted"

    # Wait for the job to be processed as if it was not cancelled
    time.sleep(JOB_PROCESSING_TIME + OPERATE_QUEUE_INTERVAL + TINY_BUFFER)
    job = retrieve_existing_job(job_management_port, job_id)
    assert (
        job.job_status == JobStatus.Cancelled
    ), "Job status should remain cancelled after processing attempt post-cancellation"


def test_can_cancel_running_job(job_management_port):
    job_id = add_job(job_management_port)

    # Wait for the job to be in running state
    time.sleep(JOB_PROCESSING_TIME / 2)

    job = retrieve_existing_job(job_management_port, job_id)
    assert (
        job.job_status == JobStatus.Running
    ), "Job status should be running before cancellation"

    cancel_job(job_management_port, job_id)

    job = retrieve_existing_job(job_management_port, job_id)
    assert (
        job.job_status == JobStatus.Cancelled
    ), "Job status should be cancelled after being interrupted"

    # Wait for the job to be processed as if it was not cancelled
    time.sleep(JOB_PROCESSING_TIME + OPERATE_QUEUE_INTERVAL + TINY_BUFFER)
    job = retrieve_existing_job(job_management_port, job_id)
    assert (
        job.job_status == JobStatus.Cancelled
    ), "Job status should remain cancelled after processing attempt post-cancellation"


def test_cannot_cancel_completed_job(job_management_port):
    job_id = add_job(job_management_port)

    # Wait for the job to be processed
    time.sleep(JOB_PROCESSING_TIME + OPERATE_QUEUE_INTERVAL + TINY_BUFFER)

    job = retrieve_existing_job(job_management_port, job_id)
    assert (
        job.job_status == JobStatus.Completed
    ), "Job status should be completed before cancellation"

    cancel_job(job_management_port, job_id)

    job = retrieve_existing_job(job_management_port, job_id)
    assert (
        job.job_status == JobStatus.Completed
    ), "Job status should remain completed after attempting to cancel a completed job"


def test_cannot_cancel_failed_job(job_management_port_that_fails):
    job_id = add_job(job_management_port_that_fails)

    # Wait for the job to be processed
    time.sleep(JOB_PROCESSING_TIME + OPERATE_QUEUE_INTERVAL + TINY_BUFFER)

    job = retrieve_existing_job(job_management_port_that_fails, job_id)
    assert (
        job.job_status == JobStatus.Failed
    ), "Job status should be failed before cancellation"

    cancel_job(job_management_port_that_fails, job_id)

    job = retrieve_existing_job(job_management_port_that_fails, job_id)
    assert (
        job.job_status == JobStatus.Failed
    ), "Job status should remain failed after attempting to cancel a failed job"


def test_process_job_in_input_order(job_management_port):
    job_id_1 = add_job(job_management_port)
    job_id_2 = add_job(job_management_port)

    # Wait for the first job to complete
    time.sleep(JOB_PROCESSING_TIME + OPERATE_QUEUE_INTERVAL + TINY_BUFFER)
    job_1 = retrieve_existing_job(job_management_port, job_id_1)
    assert (
        job_1.job_status == JobStatus.Completed
    ), "First job should run first and completed"
    job_2 = retrieve_existing_job(job_management_port, job_id_2)
    assert (
        job_2.job_status == JobStatus.Running
    ), "Second job should be running after first job completion"

    # Wait for the second job to complete
    time.sleep(JOB_PROCESSING_TIME + TINY_BUFFER)
    job_2 = retrieve_existing_job(job_management_port, job_id_2)
    assert (
        job_2.job_status == JobStatus.Completed
    ), "Second job status should be completed after processing"


def test_job_queue_shifts_correctly(job_management_port):
    job_id_1 = add_job(job_management_port)
    job_id_2 = add_job(job_management_port)

    # The second job should be second in the queue
    job_2 = retrieve_existing_job(job_management_port, job_id_2)
    assert (
        job_2.job_status == JobStatus.Waiting
    ), "Second job should be waiting after being added"
    assert isinstance(
        job_2.job_info, WaitingJob
    ), "Job info should be of type WaitingJob"
    assert (
        job_2.job_info.place_in_queue == 2
    ), "Second job should be second in the queue"

    # Wait for the first job to be running
    time.sleep(JOB_PROCESSING_TIME / 2)

    # The first job should be running
    job_1 = retrieve_existing_job(job_management_port, job_id_1)
    assert (
        job_1.job_status == JobStatus.Running
    ), "First job should be running after being started"

    # The second job should be first in the queue
    job_2 = retrieve_existing_job(job_management_port, job_id_2)
    assert (
        job_2.job_status == JobStatus.Waiting
    ), "Second job should be waiting after first job processing"
    assert isinstance(
        job_2.job_info, WaitingJob
    ), "Job info should be of type WaitingJob"
    assert job_2.job_info.place_in_queue == 1, "Second job should be first in the queue"


def test_can_retrieve_job_and_resources_at_or_before_retain_time(
    job_management_port, image_accessor_port
):
    job_id, job = add_and_complete_job(job_management_port)
    resources = job.job_result.generated_word_locations

    # Wait for some time less than MAX_RETAIN_TIME
    time.sleep(MAX_RETAIN_TIME - TINY_BUFFER)

    # Try to retrieve the job again
    job = job_management_port.retrieve_job(job_id)
    assert job is not None, "Job should still be retrievable within retain time"

    # Try to retrieve the resources
    for word_location in resources:
        if word_location.image_id is not None:
            image = image_accessor_port.get_image(word_location.image_id)
            assert (
                image is not None
            ), f"Image data should be retrievable for word '{word_location.word}'"


def test_no_guarantee_of_retrieving_job_and_resources_between_once_and_twice_the_retain_time(
    job_management_port, image_accessor_port
):
    job_id, job = add_and_complete_job(job_management_port)
    resources = job.job_result.generated_word_locations

    # Wait between once and twice the MAX_RETAIN_TIME
    time.sleep(MAX_RETAIN_TIME + TINY_BUFFER)

    # Try to retrieve the job again
    job = job_management_port.retrieve_job(job_id)
    assert (
        job is not None or job is None
    ), "Job may or may not be retrievable after once the retain time has passed"

    # Try to retrieve the resources
    for word_location in resources:
        if word_location.image_id is not None:
            image = image_accessor_port.get_image(word_location.image_id)
            assert (
                image is not None or image is None
            ), f"Image data may or may not be retrievable for word '{word_location.word}'"


def test_cannot_retrieve_job_and_resources_after_twice_the_retain_time(
    job_management_port, image_accessor_port
):
    job_id, job = add_and_complete_job(job_management_port)
    resources = job.job_result.generated_word_locations

    # Wait for the job to be processed
    time.sleep(JOB_PROCESSING_TIME + OPERATE_QUEUE_INTERVAL + TINY_BUFFER)

    # Wait for more than twice the MAX_RETAIN_TIME
    time.sleep(MAX_RETAIN_TIME * 2 + TINY_BUFFER)

    # Try to retrieve the job again
    job = job_management_port.retrieve_job(job_id)
    assert job is None, "Job should not be retrievable after retain time"

    # Try to retrieve the resources
    for word_location in resources:
        if word_location.image_id is not None:
            image = image_accessor_port.get_image(word_location.image_id)
            assert (
                image is None
            ), f"Image data should not be retrievable for word '{word_location.word}'"
