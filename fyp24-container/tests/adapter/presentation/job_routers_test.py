import time
from datetime import datetime
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from adapter.presentation.dependencies import (
    get_font_gen_service_config,
    get_image_repository_port,
    get_text_generator_port,
)
from app import app
from tests.adapter.presentation.test_dependencies import (
    JOB_PROCESSING_TIME,
    OPERATE_QUEUE_INTERVAL,
    TINY_BUFFER,
    override_font_gen_service_config,
    override_image_repository_port,
    override_text_generator_port,
    override_text_generator_port_that_fails,
    reset_all_test_dependencies,
)

### Dependency Overrides ###


def setup_default_dependency_overrides():
    """Set up dependency overrides for testing.
    If dependencies are overridden in other tests using the FastAPI object,
    this function should be called to reset them.
    """

    app.dependency_overrides = {}

    app.dependency_overrides[get_text_generator_port] = override_text_generator_port
    app.dependency_overrides[get_image_repository_port] = override_image_repository_port
    app.dependency_overrides[get_font_gen_service_config] = (
        override_font_gen_service_config
    )


### Fixtures ###


@pytest.fixture
def test_client():
    client = TestClient(app)

    reset_all_test_dependencies()

    setup_default_dependency_overrides()

    return client


### Helper Functions ###


def is_valid_uuid(val):
    try:
        UUID(val)
        return True
    except ValueError:
        return False


def is_valid_datetime(date_str):
    try:
        datetime.fromisoformat(date_str)
        return True
    except ValueError:
        return False


def assert_job_result_is_valid(job_result):
    assert type(job_result["generated_word_locations"]) is list
    for word_location in job_result["generated_word_locations"]:
        assert type(word_location["word"]) is str
        assert type(word_location["success"] is bool)
        assert word_location["image_id"] is None or is_valid_uuid(
            word_location["image_id"]
        )


### Tests ###


def test_start_job_with_valid_input(test_client):
    response = test_client.post("/start_job", json={"input_text": ""})
    assert response.status_code == 200
    assert "job_id" in response.json()
    assert is_valid_uuid(response.json()["job_id"])


def test_start_job_with_invalid_input(test_client):
    response = test_client.post("/start_job")
    assert response.status_code == 422
    assert response.json()["detail"][0]["msg"] == "Field required"


def test_interrupt_non_existent_job(test_client):
    response = test_client.post(
        "/interrupt_job", json={"job_id": "12345678-1234-5678-1234-567812345678"}
    )
    assert response.status_code == 200
    assert response.json() == {}


def test_interrupt_existent_job(test_client):
    # Start a job
    start_response = test_client.post("/start_job", json={"input_text": ""})
    assert start_response.status_code == 200
    job_id = start_response.json()["job_id"]

    # Interrupt the job
    response = test_client.post("/interrupt_job", json={"job_id": job_id})
    assert response.status_code == 200
    assert response.json() == {}


def test_interrupt_job_with_invalid_id(test_client):
    response = test_client.post("/interrupt_job", json={"job_id": "invalid-id"})
    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid ID format"}


def test_retrieve_non_existent_job(test_client):
    response = test_client.get(
        "/retrieve_job", params={"job_id": "12345678-1234-5678-1234-567812345678"}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Job not found"}


def test_retrieve_existent_job(test_client):
    # Start a job
    start_response = test_client.post("/start_job", json={"input_text": ""})
    assert start_response.status_code == 200
    job_id = start_response.json()["job_id"]

    # Retrieve the job
    response = test_client.get("/retrieve_job", params={"job_id": job_id})
    assert response.status_code == 200

    response_body = response.json()
    assert response_body["job_id"] == job_id


def test_retrieve_running_job(test_client):
    # Start a job
    start_response = test_client.post("/start_job", json={"input_text": "中文字"})
    assert start_response.status_code == 200
    job_id = start_response.json()["job_id"]

    # Wait for the job to be started
    time.sleep(JOB_PROCESSING_TIME / 2)

    # Retrieve the job
    response = test_client.get("/retrieve_job", params={"job_id": job_id})
    assert response.status_code == 200

    response_body = response.json()
    assert response_body["job_id"] == job_id
    assert response_body["job_input"] == {"input_text": "中文字"}
    assert response_body["job_status"] == "running"

    assert is_valid_datetime(response_body["job_info"]["time_start_to_queue"])
    assert is_valid_datetime(response_body["job_info"]["time_start_to_run"])
    assert type(response_body["job_info"]["running_state"]["name"]) is str
    assert type(response_body["job_info"]["running_state"]["message"]) is str

    assert_job_result_is_valid(response_body["job_result"])


def test_retrieve_waiting_job(test_client):
    # Start two jobs
    start_response = test_client.post("/start_job", json={"input_text": "中文字"})
    assert start_response.status_code == 200
    job_id = start_response.json()["job_id"]

    start_response_2 = test_client.post("/start_job", json={"input_text": "中文字"})
    assert start_response_2.status_code == 200
    job_id_2 = start_response_2.json()["job_id"]

    # Wait for the first job to be started
    time.sleep(JOB_PROCESSING_TIME / 2)

    # Ensure the first job is running
    response = test_client.get("/retrieve_job", params={"job_id": job_id})
    assert response.status_code == 200

    assert response.json()["job_status"] == "running"

    # Retrieve the second job
    response_2 = test_client.get("/retrieve_job", params={"job_id": job_id_2})
    assert response_2.status_code == 200

    response_body = response_2.json()
    assert response_body["job_id"] == job_id_2
    assert response_body["job_input"] == {"input_text": "中文字"}
    assert response_body["job_status"] == "waiting"

    assert is_valid_datetime(response_body["job_info"]["time_start_to_queue"])
    assert response_body["job_info"]["place_in_queue"] == 1

    assert response_body["job_result"] == {"generated_word_locations": []}


def test_retrieve_completed_job(test_client):
    # Start a job
    start_response = test_client.post("/start_job", json={"input_text": "中文字"})
    assert start_response.status_code == 200
    job_id = start_response.json()["job_id"]

    # Wait for the job to be processed
    time.sleep(JOB_PROCESSING_TIME + OPERATE_QUEUE_INTERVAL + TINY_BUFFER)

    # Retrieve the job
    response = test_client.get("/retrieve_job", params={"job_id": job_id})
    assert response.status_code == 200

    response_body = response.json()
    assert response_body["job_id"] == job_id
    assert response_body["job_input"] == {"input_text": "中文字"}
    assert response_body["job_status"] == "completed"

    assert is_valid_datetime(response_body["job_info"]["time_start_to_queue"])
    assert is_valid_datetime(response_body["job_info"]["time_start_to_run"])
    assert is_valid_datetime(response_body["job_info"]["time_end"])

    assert_job_result_is_valid(response_body["job_result"])


def test_retrieve_failed_job(test_client):
    # Modify the dependency override to simulate a failure
    app.dependency_overrides[get_text_generator_port] = (
        override_text_generator_port_that_fails
    )

    # Start a job
    start_response = test_client.post("/start_job", json={"input_text": "中文字"})
    assert start_response.status_code == 200
    job_id = start_response.json()["job_id"]

    # Wait for the job to be processed
    time.sleep(JOB_PROCESSING_TIME + OPERATE_QUEUE_INTERVAL + TINY_BUFFER)

    # Retrieve the job
    response = test_client.get("/retrieve_job", params={"job_id": job_id})
    assert response.status_code == 200

    response_body = response.json()
    assert response_body["job_id"] == job_id
    assert response_body["job_input"] == {"input_text": "中文字"}
    assert response_body["job_status"] == "failed"

    assert is_valid_datetime(response_body["job_info"]["time_start_to_queue"])
    assert is_valid_datetime(response_body["job_info"]["time_start_to_run"])
    assert is_valid_datetime(response_body["job_info"]["time_end"])
    assert type(response_body["job_info"]["error_message"]) is str

    assert_job_result_is_valid(response_body["job_result"])


def test_retrieve_cancelled_job(test_client):
    # Start a job
    start_response = test_client.post("/start_job", json={"input_text": "中文字"})
    assert start_response.status_code == 200
    job_id = start_response.json()["job_id"]

    # Ensure the job is waiting or running
    response = test_client.get("/retrieve_job", params={"job_id": job_id})
    assert response.status_code == 200
    assert response.json()["job_status"] in ["waiting", "running"]

    # Cancel the job
    response = test_client.post("/interrupt_job", json={"job_id": job_id})
    assert response.status_code == 200
    assert response.json() == {}

    # Retrieve the cancelled job
    response = test_client.get("/retrieve_job", params={"job_id": job_id})
    assert response.status_code == 200

    response_body = response.json()
    assert response_body["job_id"] == job_id
    assert response_body["job_input"] == {"input_text": "中文字"}
    assert response_body["job_status"] == "cancelled"

    assert is_valid_datetime(response_body["job_info"]["time_start_to_queue"])
    assert response_body["job_info"]["time_start_to_run"] is None or is_valid_datetime(
        response_body["job_info"]["time_start_to_run"]
    )
    assert is_valid_datetime(response_body["job_info"]["time_end"])

    assert_job_result_is_valid(response_body["job_result"])
