from typing import Optional
from uuid import UUID

from application.port_out.image_repository_port import ImageRepositoryPort
from domain.value.image_data import ImageData


class ImageRepositoryMock(ImageRepositoryPort):
    __files: dict[UUID, ImageData]

    def __init__(self):
        self.__files = {}

    def get_image(self, image_id: UUID) -> Optional[ImageData]:
        return self.__files.get(image_id, None)

    def save_image(self, image_data: ImageData) -> None:
        self.__files[image_data.image_id] = image_data

    def delete_image(self, image_id: UUID) -> None:
        if image_id in self.__files:
            del self.__files[image_id]
