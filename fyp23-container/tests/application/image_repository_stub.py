from typing import Optional
from uuid import UUID, uuid4

from application.port_out.image_repository_port import ImageRepositoryPort


class ImageRepositoryStub(ImageRepositoryPort):
    __files: dict[UUID, bytes]

    def __init__(self):
        self.__files = {}

    def get_image(self, image_id: UUID) -> Optional[bytes]:
        return self.__files.get(image_id, None)

    def save_image(self, image: bytes) -> UUID:
        image_id = uuid4()
        self.__files[image_id] = image
        return image_id

    def save_image_to_id(self, image: bytes, image_id: UUID) -> None:
        self.__files[image_id] = image

    def delete_image(self, image_id: UUID) -> None:
        if image_id in self.__files:
            del self.__files[image_id]
