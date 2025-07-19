import io
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from adapter.presentation.dependencies import get_image_repository_port
from app import app
from tests.adapter.presentation.test_dependencies import (
    override_image_repository_port,
    reset_all_test_dependencies,
)

### Dependency Overrides ###


def setup_default_dependency_overrides():
    """Set up dependency overrides for testing."""

    app.dependency_overrides[get_image_repository_port] = override_image_repository_port


### Fixtures ###


@pytest.fixture
def test_client():
    client = TestClient(app)

    reset_all_test_dependencies()

    setup_default_dependency_overrides()

    return client


@pytest.fixture
def store_mock_png():
    image = Image.new("RGB", (100, 100), color=0)

    mock_image_bytes = convert_image_to_bytes(image=image, format="PNG")

    mock_image_id = override_image_repository_port().save_image(image=mock_image_bytes)
    return mock_image_id, mock_image_bytes


@pytest.fixture
def store_mock_jpeg():
    image = Image.new("RGB", (100, 100), color=0)

    mock_image_bytes = convert_image_to_bytes(image=image, format="JPEG")

    mock_image_id = override_image_repository_port().save_image(image=mock_image_bytes)
    return mock_image_id, mock_image_bytes


### Helper Functions ###


def convert_image_to_bytes(image, format):
    image_stream = io.BytesIO()
    image.save(image_stream, format=format)
    image_stream.seek(0)
    mock_image_bytes = image_stream.getvalue()
    return mock_image_bytes


### Tests ###


def test_get_non_existent_image(test_client, store_mock_png, store_mock_jpeg):
    response = test_client.get(
        "/get_image", params={"image_id": UUID("12345678-1234-5678-1234-567812345678")}
    )
    assert response.status_code == 404
    assert response.json() == {"detail": "Image not found"}


def test_get_image_with_invalid_id(test_client, store_mock_png, store_mock_jpeg):
    response = test_client.get("/get_image", params={"image_id": "invalid_uuid"})
    assert response.status_code == 422
    assert response.json() == {"detail": "Invalid ID format"}


def test_get_existing_png_image(test_client, store_mock_png, store_mock_jpeg):
    mock_image_id, mock_image = store_mock_png
    response = test_client.get("/get_image", params={"image_id": str(mock_image_id)})

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/png"
    assert response.content == mock_image


def test_get_existing_jpeg_image(test_client, store_mock_png, store_mock_jpeg):
    mock_image_id, mock_image = store_mock_jpeg
    response = test_client.get("/get_image", params={"image_id": str(mock_image_id)})

    assert response.status_code == 200
    assert response.headers["Content-Type"] == "image/jpeg"
    assert response.content == mock_image
