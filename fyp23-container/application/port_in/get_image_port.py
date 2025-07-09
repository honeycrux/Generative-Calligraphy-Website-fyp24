from abc import ABC
from uuid import UUID
from typing import Optional

from domain.value.image_data import ImageData


class GetImagePort(ABC):
    """
    Port for retrieving images.
    This port defines the interface for getting images by their ID.
    """

    def get_image(self, image_id: UUID) -> Optional[ImageData]:
        """
        Retrieve an image by its ID.

        :param image_id: The ID of the image to retrieve.
        :return: The image if found, otherwise None.
        """
        pass
