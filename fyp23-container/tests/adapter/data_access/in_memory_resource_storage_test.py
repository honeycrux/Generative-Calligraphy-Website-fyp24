import pytest
from uuid import UUID

from adapter.data_access.in_memory_resource_storage import InMemoryResourceStorage


### Fixtures ###


@pytest.fixture
def in_memory_resource_storage():
    return InMemoryResourceStorage()


### Tests ###


def test_cannot_get_non_existent_image(in_memory_resource_storage):
    mock_image_id = UUID("12345678-1234-5678-1234-567812345678")
    retrieved_image = in_memory_resource_storage.get_image(mock_image_id)
    assert retrieved_image is None, "Expected None when retrieving a non-existent image"


def test_can_save_and_get_image(in_memory_resource_storage):
    mock_word_image = b"mock_word_image"

    mock_image_id = in_memory_resource_storage.save_image(mock_word_image)

    retrieved_image = in_memory_resource_storage.get_image(mock_image_id)
    assert retrieved_image is not None, "Expected image to be found after saving"
    assert (
        retrieved_image == mock_word_image
    ), "Expected retrieved image bytes to match saved data"


def test_saving_image_overwrites_existing_image(in_memory_resource_storage):
    initial_word_image = b"initial_word_image"
    updated_word_image = b"updated_word_image"

    # Save initial image
    mock_image_id = in_memory_resource_storage.save_image(initial_word_image)

    # Save updated image
    in_memory_resource_storage.save_image_to_id(
        image=updated_word_image, image_id=mock_image_id
    )

    retrieved_image = in_memory_resource_storage.get_image(mock_image_id)
    assert retrieved_image is not None, "Expected image to be found after saving"
    assert (
        retrieved_image == updated_word_image
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
    mock_word_image = b"mock_word_image"

    mock_image_id = in_memory_resource_storage.save_image(mock_word_image)

    retrieved_image_before_delete = in_memory_resource_storage.get_image(mock_image_id)
    assert (
        retrieved_image_before_delete is not None
    ), "Expected image to exist before delete"

    in_memory_resource_storage.delete_image(mock_image_id)

    retrieved_image_after_delete = in_memory_resource_storage.get_image(mock_image_id)
    assert (
        retrieved_image_after_delete is None
    ), "Expected image to be None after delete"
