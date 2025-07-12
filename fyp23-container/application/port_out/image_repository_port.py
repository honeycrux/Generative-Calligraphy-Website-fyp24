from abc import ABC, abstractmethod
from typing import Optional
from uuid import UUID


class ImageRepositoryPort(ABC):
    """
    Port for image repository.
    This port defines the interface for accessing and managing images.
    """

    @abstractmethod
    def get_image(self, image_id: UUID) -> Optional[bytes]:
        """
        Retrieve an image by its ID.

        :param image_id: The ID of the image to retrieve.
        :return: The image data if found, otherwise None.
        """
        pass

    @abstractmethod
    def save_image(self, image: bytes) -> UUID:
        """
        Save an image.

        :param image: The data of the image to save.
        :return: The ID of the saved image.
        """
        pass

    @abstractmethod
    def save_image_to_id(self, image: bytes, image_id: UUID) -> None:
        """
        Save an image to a specific ID.
        This will overwrite any existing image with the same ID.

        :param image: The data of the image to save.
        :param image_id: The ID to save the image under.
        """
        pass

    @abstractmethod
    def delete_image(self, image_id: UUID) -> None:
        """
        Delete an image by its ID.

        :param image_id: The ID of the image to delete.
        """
        pass
