from uuid import UUID
import pytest
from PIL import Image

from application.port_in.get_image_port import GetImagePort
from application.port_out.image_repository_port import ImageRepositoryPort
from application.get_image_service import GetImageService
from domain.value.image_data import ImageData
from tests.mocks.image_repository_mock import ImageRepositoryMock


### Fixtures ###


@pytest.fixture
def image_repository_port() -> ImageRepositoryPort:
    image_repository_mock = ImageRepositoryMock()

    # Add a mock image to the repository
    mock_image_id = UUID("12345678-1234-5678-1234-567812345678")
    mock_image = Image.new("RGBA", size=(0, 0), color=0)
    image_repository_mock.save_image(
        ImageData(image_id=mock_image_id, image=mock_image)
    )

    return image_repository_mock


@pytest.fixture
def get_image_port(image_repository_port) -> GetImagePort:
    return GetImageService(image_repository_port=image_repository_port)


### Tests ###


def test_returns_none_for_non_existent_image(get_image_port) -> None:
    image_id = UUID("87654321-4321-6789-4321-678987654321")
    image = get_image_port.get_image(image_id)
    assert image is None


def test_returns_image_for_existent_image(get_image_port) -> None:
    image_id = UUID("12345678-1234-5678-1234-567812345678")
    image = get_image_port.get_image(image_id)
    assert image is not None
    assert image.image_id == image_id
