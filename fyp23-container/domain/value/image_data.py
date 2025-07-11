from uuid import UUID, uuid4
from pydantic import BaseModel, ConfigDict


class ImageData(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    image_id: UUID
    image_bytes: bytes

    @staticmethod
    def new(image_bytes: bytes) -> "ImageData":
        """Create a new ImageData instance with a generated UUID."""
        return ImageData(image_id=uuid4(), image_bytes=image_bytes)
