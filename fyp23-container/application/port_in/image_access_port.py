from abc import ABC, abstractmethod
from uuid import UUID
from typing import Optional


class ImageAccessPort(ABC):
    """
    Port for retrieving images.
    This port defines the interface for getting images by their ID.
    """

    @abstractmethod
    def get_image(self, image_id: UUID) -> Optional[bytes]:
        """
        Retrieve an image by its ID.

        :param image_id: The ID of the image to retrieve.
        :return: The image if found, otherwise None.
        """
        pass
