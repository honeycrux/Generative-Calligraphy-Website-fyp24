from dataclasses import dataclass
from uuid import UUID
from PIL import Image


@dataclass(frozen=True)
class ImageData:
    image_id: UUID
    image: Image.Image
