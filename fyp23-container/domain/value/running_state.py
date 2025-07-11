from enum import Enum
from pydantic import BaseModel, ConfigDict


class RunningState(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    name: str
    message: str

    @staticmethod
    def not_started() -> "RunningState":
        return RunningState(
            name="NOT_STARTED", message="Generation has not started yet."
        )

    @staticmethod
    def generating(current: int, total: int) -> "RunningState":
        return RunningState(
            name="GENERATING", message=f"Generating {current}/{total} characters."
        )

    @staticmethod
    def cleaning_up() -> "RunningState":
        return RunningState(name="CLEANING_UP", message="Cleaning up.")
