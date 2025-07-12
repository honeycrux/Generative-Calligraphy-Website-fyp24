from uuid import UUID
import pytest
from PIL import Image

from application.port_in.image_access_port import ImageAccessPort
from application.port_out.image_repository_port import ImageRepositoryPort
from application.image_access_service import ImageAccessService
from tests.application.image_repository_mock import ImageRepositoryMock


### Fixtures ###


@pytest.fixture
def mock_image_1() -> tuple[UUID, bytes]:
    image_id = UUID("12345678-1234-5678-1234-567812345678")
    mock_image = Image.new("RGBA", size=(0, 0), color=0).tobytes()
    return image_id, mock_image


@pytest.fixture
def image_repository_port(mock_image_1) -> ImageRepositoryPort:
    image_repository_mock = ImageRepositoryMock()
    mock_image_id, mock_image = mock_image_1

    # Add a mock image to the repository
    image_repository_mock.save_image_to_id(image=mock_image, image_id=mock_image_id)

    return image_repository_mock


@pytest.fixture
def image_access_port(image_repository_port) -> ImageAccessPort:
    return ImageAccessService(image_repository_port=image_repository_port)


### Tests ###


def test_returns_none_for_non_existent_image(image_access_port) -> None:
    image_id = UUID("87654321-4321-6789-4321-678987654321")
    image = image_access_port.get_image(image_id)
    assert image is None, "Expected None when retrieving a non-existent image"


def test_returns_image_for_existent_image(image_access_port, mock_image_1) -> None:
    mock_image_id, mock_image = mock_image_1
    image = image_access_port.get_image(mock_image_id)
    assert image is not None, "Expected image to be found"
    assert image == mock_image, "Expected retrieved image bytes to match saved data"
