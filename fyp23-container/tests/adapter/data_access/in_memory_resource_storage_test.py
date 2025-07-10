import pytest
from uuid import UUID

from adapter.data_access.in_memory_resource_storage import InMemoryResourceStorage
from domain.value.image_data import ImageData


@pytest.fixture
def in_memory_resource_storage():
    return InMemoryResourceStorage()


def test_cannot_get_non_existent_image(in_memory_resource_storage):
    mock_image_id = UUID("12345678-1234-5678-1234-567812345678")
    retrieved_image = in_memory_resource_storage.get_image(mock_image_id)
    assert retrieved_image is None, "Expected None when retrieving a non-existent image"


def test_can_save_and_get_image(in_memory_resource_storage):
    mock_image_id = UUID("12345678-1234-5678-1234-567812345678")
    mock_image_data = b"mock_image_data"

    image_data = ImageData(image_id=mock_image_id, image_bytes=mock_image_data)
    in_memory_resource_storage.save_image(image_data)

    retrieved_image = in_memory_resource_storage.get_image(mock_image_id)
    assert retrieved_image is not None, "Expected image to be found after saving"
    assert (
        retrieved_image.image_bytes == mock_image_data
    ), "Expected retrieved image bytes to match saved data"


def test_saving_image_overwrites_existing_image(in_memory_resource_storage):
    mock_image_id = UUID("12345678-1234-5678-1234-567812345678")
    initial_image_data = b"initial_image_data"
    updated_image_data = b"updated_image_data"

    # Save initial image
    in_memory_resource_storage.save_image(
        ImageData(image_id=mock_image_id, image_bytes=initial_image_data)
    )

    # Save updated image
    in_memory_resource_storage.save_image(
        ImageData(image_id=mock_image_id, image_bytes=updated_image_data)
    )

    retrieved_image = in_memory_resource_storage.get_image(mock_image_id)
    assert retrieved_image is not None, "Expected image to be found after saving"
    assert (
        retrieved_image.image_bytes == updated_image_data
    ), "Expected retrieved image bytes to match updated data"


def test_cannot_delete_non_existent_image(in_memory_resource_storage):
    mock_image_id = UUID("12345678-1234-5678-1234-567812345678")

    # Attempt to delete a non-existent image
    in_memory_resource_storage.delete_image(mock_image_id)

    # Verify that no exception is raised and the state remains unchanged
    retrieved_image = in_memory_resource_storage.get_image(mock_image_id)
    assert (
        retrieved_image is None
    ), "Expected no image to be found after deletion attempt"


def test_can_delete_image(in_memory_resource_storage):
    mock_image_id = UUID("12345678-1234-5678-1234-567812345678")
    mock_image_data = b"mock_image_data"

    in_memory_resource_storage.save_image(
        ImageData(image_id=mock_image_id, image_bytes=mock_image_data)
    )

    retrieved_image_before_delete = in_memory_resource_storage.get_image(mock_image_id)
    assert (
        retrieved_image_before_delete is not None
    ), "Expected image to exist before delete"

    in_memory_resource_storage.delete_image(mock_image_id)

    retrieved_image_after_delete = in_memory_resource_storage.get_image(mock_image_id)
    assert (
        retrieved_image_after_delete is None
    ), "Expected image to be None after delete"
