import io
import os
import time
from uuid import UUID

import pytest
import torch
from fastapi.testclient import TestClient
from PIL import Image

from adapter.presentation.dependencies import reset_all_dependencies
from app import app

### Constants ###


TEST_OUTPUT_FOLDER = "test_outputs/app_integration_test"

# my tests usually finish in under 45s; adjust if necessary
CPU_GENERATION_TIMEOUT = 60  # seconds

# my tests usually finish in under 15s; adjust if necessary
GPU_GENERATION_TIMEOUT = 30  # seconds

active_generation_timeout = (
    GPU_GENERATION_TIMEOUT if torch.cuda.is_available() else CPU_GENERATION_TIMEOUT
)


### Dependency Overrides ###


def setup_default_dependency_overrides():
    """Set up dependency overrides for testing.
    If dependencies are overridden in other tests using the FastAPI object,
    this function should be called to reset them.
    """

    app.dependency_overrides = {}


### Fixtures ###


@pytest.fixture(autouse=True)
def setup_output_folder():
    os.makedirs(TEST_OUTPUT_FOLDER, exist_ok=True)
    os.chmod("test_outputs/", 0o777)
    os.chmod(TEST_OUTPUT_FOLDER, 0o777)


@pytest.fixture
def test_client():
    client = TestClient(app)

    reset_all_dependencies()

    setup_default_dependency_overrides()

    return client


### Helper Functions ###


def is_valid_uuid(val):
    try:
        UUID(val)
        return True
    except ValueError:
        return False


def remove_existing_file(image_save_path):
    if os.path.isfile(image_save_path):
        os.remove(image_save_path)


def save_image(image: Image.Image, image_save_path: str):
    image.save(image_save_path)
    os.chmod(image_save_path, 0o777)


### Tests ###


@pytest.mark.slow
@pytest.mark.timeout(active_generation_timeout)  # seconds
def test_text_generation_process(test_client):
    image_save_path = f"{TEST_OUTPUT_FOLDER}/test_text_generation_process.png"

    remove_existing_file(image_save_path)

    start_job_response = test_client.post(
        "/start_job",
        json={
            "input_text": "書",
        },
    )

    assert start_job_response.status_code == 200
    job_id = start_job_response.json()["job_id"]
    assert isinstance(job_id, str)

    job_finished = False
    retrieve_job_response = None

    while not job_finished:
        retrieve_job_response = test_client.get(
            f"/retrieve_job", params={"job_id": job_id}
        )
        assert retrieve_job_response.status_code == 200
        job_finished = retrieve_job_response.json()["job_status"] not in [
            "waiting",
            "running",
        ]
        time.sleep(0.5)

    assert retrieve_job_response is not None
    assert retrieve_job_response.json()["job_status"] == "completed"

    job_result = retrieve_job_response.json()["job_result"]

    assert job_result["generated_word_locations"][0]["word"] == "書"
    assert job_result["generated_word_locations"][0]["success"] is True
    image_id = job_result["generated_word_locations"][0]["image_id"]
    assert is_valid_uuid(image_id)

    get_image_response = test_client.get(f"/get_image", params={"image_id": image_id})
    if get_image_response.status_code != 200:
        raise Exception(f"Failed to retrieve image: {get_image_response.json()}")
    assert get_image_response.status_code == 200
    image = Image.open(io.BytesIO(get_image_response.content))
    image.save(image_save_path)
