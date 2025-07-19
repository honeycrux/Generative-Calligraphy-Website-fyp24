from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class GeneratedWordLocation(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    word: str
    success: bool
    image_id: Optional[UUID]

    def __init__(self, word: str, image_id: Optional[UUID]):
        if len(word) != 1:
            raise ValueError("Word must be a single character, got: {}".format(word))

        success = image_id is not None

        super().__init__(word=word, success=success, image_id=image_id)
