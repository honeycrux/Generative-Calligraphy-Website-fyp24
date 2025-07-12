from uuid import UUID
from typing import Optional

from application.port_in.image_access_port import ImageAccessPort
from application.port_out.image_repository_port import ImageRepositoryPort


class ImageAccessService(ImageAccessPort):
    __image_repository_port: ImageRepositoryPort

    def __init__(self, image_repository_port: ImageRepositoryPort) -> None:
        self.__image_repository_port = image_repository_port

    def get_image(self, image_id: UUID) -> Optional[bytes]:
        return self.__image_repository_port.get_image(image_id)
