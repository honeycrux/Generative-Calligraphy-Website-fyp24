from typing import Optional
from pydantic import BaseModel, ConfigDict


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
