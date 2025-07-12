from asyncio import Task
import asyncio
from typing import Callable, Union
from PIL import Image

from application.port_out.text_generator_port import (
    TextGeneratorPort,
)
from domain.value.job_info import RunningJob
from domain.value.job_input import JobInput
from domain.value.running_state import RunningState
from domain.value.generated_word import GeneratedWord


class FontGenerationApplicationWithProgressMock(TextGeneratorPort):
    __progress_interval: float  # Simulated progress interval

    def __init__(self, progress_interval: float):
        super().__init__()
        self.__progress_interval = progress_interval

    async def __generation(
        self,
        job_input: JobInput,
        job_info: RunningJob,
        on_new_state: Callable[[RunningState], None],
        on_new_word_result: Callable[[GeneratedWord], None],
    ) -> Union[bool, str]:
        total_chars = len(job_input.input_text)

        on_new_state(RunningState.generating(current=0, total=total_chars))

        # Simulate generation of each character
        for idx, char in enumerate(job_input.input_text):
            # Simulate async operation
            await asyncio.sleep(self.__progress_interval)

            mock_image = Image.new("RGBA", size=(0, 0), color=0)

            on_new_state(RunningState.generating(current=idx + 1, total=total_chars))

            on_new_word_result(
                GeneratedWord(
                    word=char,
                    image=mock_image.tobytes(),
                )
            )

        on_new_state(RunningState.cleaning_up())

        return True

    def generate_text(
        self,
        job_input: JobInput,
        job_info: RunningJob,
        on_new_state: Callable[[RunningState], None],
        on_new_word_result: Callable[[GeneratedWord], None],
    ) -> Task[Union[bool, str]]:
        return asyncio.create_task(
            self.__generation(
                job_input=job_input,
                job_info=job_info,
                on_new_state=on_new_state,
                on_new_word_result=on_new_word_result,
            )
        )
