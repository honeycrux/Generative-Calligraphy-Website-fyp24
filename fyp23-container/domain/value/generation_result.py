from uuid import UUID
from pydantic import BaseModel, ConfigDict
from typing import Optional


class WordResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    word: str
    success: bool
    image_id: Optional[UUID]

    def __init__(self, word: str, image_id: Optional[UUID]):
        if len(word) != 1:
            raise ValueError("Word must be a single character, got: {}".format(word))

        success = image_id is not None

        super().__init__(word=word, success=success, image_id=image_id)


class GenerationResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    word_results: list[WordResult]

    @staticmethod
    def new() -> "GenerationResult":
        return GenerationResult(word_results=[])

    def add_word_result(self, word_result: WordResult) -> None:
        self.word_results.append(word_result)
