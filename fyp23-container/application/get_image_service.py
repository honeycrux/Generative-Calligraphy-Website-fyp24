from uuid import UUID
from typing import Optional

from application.port_in.get_image_port import GetImagePort
from application.port_out.image_repository_port import ImageRepositoryPort
from domain.value.image_data import ImageData


class GetImageService(GetImagePort):
    __image_repository_port: ImageRepositoryPort

    def __init__(self, image_repository_port: ImageRepositoryPort) -> None:
        self.__image_repository_port = image_repository_port

    def get_image(self, image_id: UUID) -> Optional[ImageData]:
        return self.__image_repository_port.get_image(image_id)
