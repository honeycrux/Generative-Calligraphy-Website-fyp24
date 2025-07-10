from abc import ABC
from typing import Optional
from uuid import UUID

from domain.value.image_data import ImageData


class ImageRepositoryPort(ABC):
    """
    Port for image repository.
    This port defines the interface for accessing and managing images.
    """

    def get_image(self, image_id: UUID) -> Optional[ImageData]:
        """
        Retrieve an image by its ID.

        :param image_id: The ID of the image to retrieve.
        :return: An ImageData object if the image exists, otherwise None.
        """
        pass

    def save_image(self, image_data: ImageData) -> None:
        """
        Save an image.
        Saving to an existing ID will overwrite it.

        :param image_data: The data of the image to save.
        """
        pass

    def delete_image(self, image_id: UUID) -> None:
        """
        Delete an image by its ID.

        :param image_id: The ID of the image to delete.
        """
        pass
