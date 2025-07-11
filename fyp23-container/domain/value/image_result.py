from typing import Optional
from pydantic import BaseModel, ConfigDict

from domain.value.image_data import ImageData


class ImageResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    word: str
    success: bool
    image_data: Optional[ImageData]

    def __init__(self, word: str, image_data: Optional[ImageData]):
        if len(word) != 1:
            raise ValueError("Word must be a single character, got: {}".format(word))

        success = image_data is not None

        super().__init__(word=word, image_data=image_data, success=success)
