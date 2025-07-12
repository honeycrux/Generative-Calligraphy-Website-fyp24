from pydantic import BaseModel, ConfigDict

from domain.value.generated_word_location import GeneratedWordLocation


class JobResult(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    generated_word_locations: list[GeneratedWordLocation]

    @staticmethod
    def new() -> "JobResult":
        return JobResult(generated_word_locations=[])

    def add_word_location(self, word_location: GeneratedWordLocation) -> None:
        self.generated_word_locations.append(word_location)
