from enum import Enum
from pydantic import BaseModel, ConfigDict


class RunningStateObject(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    message: str


class RunningState(Enum):
    GENERATING = RunningStateObject(name="GENERATING", message="Generating image")
