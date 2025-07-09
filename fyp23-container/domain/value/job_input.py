from pydantic import BaseModel, ConfigDict


class JobInput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    input_text: str
