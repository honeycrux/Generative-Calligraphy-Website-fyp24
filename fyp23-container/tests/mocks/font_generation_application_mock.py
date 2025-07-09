from asyncio import Task
import asyncio
from typing import Callable, Optional, Union
from uuid import uuid4
from PIL import Image

from application.port_out.font_generation_application_port import (
    FontGenerationApplicationPort,
)
from domain.value.image_data import ImageData
from domain.value.generation_result import GenerationResult, WordResult
from domain.value.job_info import RunningJob
from domain.value.job_input import JobInput
from domain.value.running_state import RunningState


class FontGenerationApplicationMock(FontGenerationApplicationPort):
    run_seconds: float  # Simulated wait time
    simulate_success: bool  # Simulated success flag

    def __init__(self, run_seconds: float, simulate_success: bool):
        super().__init__()
        self.run_seconds = run_seconds
        self.simulate_success = simulate_success

    async def __generation(
        self,
        job_input: JobInput,
        job_info: RunningJob,
        on_new_state: Callable[[RunningState], None],
        on_new_word_result: Callable[[str, Optional[ImageData]], None],
    ) -> Union[bool, str]:
        # Simulate async operation
        await asyncio.sleep(self.run_seconds)

        if not self.simulate_success:
            # Simulate failure
            return "Simulated failure"

        # Create some characters
        for char in job_input.input_text:
            mock_image_id = uuid4()
            mock_image = Image.new("RGBA", size=(0, 0), color=0)

            on_new_word_result(
                char, ImageData(image_id=mock_image_id, image=mock_image)
            )

        return True

    def generate_font(
        self,
        job_input: JobInput,
        job_info: RunningJob,
        on_new_state: Callable[[RunningState], None],
        on_new_word_result: Callable[[str, Optional[ImageData]], None],
    ) -> Task[Union[bool, str]]:
        return asyncio.create_task(
            self.__generation(job_input, job_info, on_new_state, on_new_word_result)
        )
