import asyncio
from asyncio import Task
from typing import Callable, Union

from PIL import Image

from application.port_out.text_generator_port import TextGeneratorPort
from domain.value.generated_word import GeneratedWord
from domain.value.job_info import RunningJob
from domain.value.job_input import JobInput
from domain.value.running_state import RunningState


class TextGeneratorStub(TextGeneratorPort):
    __job_processing_time: float  # Simulated job processing time
    __simulate_success: bool  # Whether to simulate a successful job or not

    def __init__(self, job_processing_time: float, simulate_success: bool):
        super().__init__()
        self.__job_processing_time = job_processing_time
        self.__simulate_success = simulate_success

    async def __generation(
        self,
        job_input: JobInput,
        job_info: RunningJob,
        on_new_state: Callable[[RunningState], None],
        on_new_word_result: Callable[[GeneratedWord], None],
    ) -> Union[bool, str]:
        # Simulate async operation
        await asyncio.sleep(self.__job_processing_time)

        if not self.__simulate_success:
            # Simulate failure
            return "Simulated failure"

        # Create some characters
        for char in job_input.input_text:
            mock_image = Image.new("RGBA", size=(0, 0), color=0).tobytes()

            on_new_word_result(
                GeneratedWord(
                    word=char,
                    image=mock_image,
                )
            )

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
