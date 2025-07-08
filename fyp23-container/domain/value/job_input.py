from enum import Enum
from pydantic import BaseModel, ConfigDict


class FontGenModel(Enum):
    fyp23 = "fyp23"
    fyp24 = "fyp24"

    @classmethod
    def has_key(cls, key):
        return key in cls._member_names_


class JobInput(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    model_id: FontGenModel
    input_text: str
