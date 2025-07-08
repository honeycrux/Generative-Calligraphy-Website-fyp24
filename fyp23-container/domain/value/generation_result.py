from pydantic import BaseModel, ConfigDict
from typing import Optional


class WordResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    word: str
    success: bool
    url: Optional[str] = None


class GenerationResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    word_results: list[WordResult]

    @staticmethod
    def create() -> "GenerationResult":
        return GenerationResult(word_results=[])

    def add_word_result(self, word_result: WordResult) -> None:
        self.word_results.append(word_result)
