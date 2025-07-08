from asyncio import Task
import asyncio
from typing import Callable, Union

from application.port_out.font_generation_application_port import (
    FontGenerationApplicationPort,
)
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
    ) -> Union[GenerationResult, str]:
        # Simulate async operation
        await asyncio.sleep(self.run_seconds)

        if not self.simulate_success:
            # Simulate a failure
            return "Simulated failure"

        # Create a mock result
        job_id = job_info.job_id
        result = GenerationResult(
            word_results=[
                WordResult(word=char, success=True, url=f"{job_id}/{char}.png")
                for char in job_input.input_text
            ]
        )

        return result

    def generate_font(
        self,
        job_input: JobInput,
        job_info: RunningJob,
        on_new_state: Callable[[RunningState], None],
    ) -> Task[Union[GenerationResult, str]]:
        return asyncio.create_task(self.__generation(job_input, job_info, on_new_state))
