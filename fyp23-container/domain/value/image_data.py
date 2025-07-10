from uuid import UUID
from pydantic import BaseModel, ConfigDict


class ImageData(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    image_id: UUID
    image_bytes: bytes
