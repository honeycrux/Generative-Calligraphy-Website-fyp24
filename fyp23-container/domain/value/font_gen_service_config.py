from pydantic import BaseModel


class FontGenServiceConfig(BaseModel):
    model_config = {"frozen": True, "extra": "forbid"}

    operate_queue_interval: float  # seconds to wait if the queue is empty
    max_retain_time: float  # seconds to retain stopped jobs

    def __init__(self, **data):
        super().__init__(**data)
        if self.operate_queue_interval < 0:
            raise ValueError("operate_queue_interval must not be negative")
        if self.operate_queue_interval == 0:
            raise ValueError(
                "operate_queue_interval cannot be zero: it will block the CPU indefinitely"
            )
        if self.max_retain_time < 0:
            raise ValueError("max_retain_time must not be negative")
        if self.max_retain_time == 0:
            raise ValueError(
                "max_retain_time cannot be zero: it will block the CPU indefinitely"
            )
