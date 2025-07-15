import io
from typing import Optional

from PIL import Image
from pydantic import BaseModel, ConfigDict

IMAGE_FORMAT = "PNG"


class GeneratedWord(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    word: str
    success: bool
    image: Optional[bytes]

    def __init__(self, word: str, image: Optional[bytes]):
        if len(word) != 1:
            raise ValueError("Word must be a single character, got: {}".format(word))

        success = image is not None

        super().__init__(word=word, image=image, success=success)

    @staticmethod
    def from_image(word: str, image: Optional[Image.Image]) -> "GeneratedWord":
        if image is not None:
            image_stream = io.BytesIO()
            image.save(image_stream, format=IMAGE_FORMAT)
            image_stream.seek(0)
            image_bytes = image_stream.getvalue()
        else:
            image_bytes = None

        return GeneratedWord(word=word, image=image_bytes)
