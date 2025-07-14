import asyncio
from asyncio import Task
from typing import Callable, Optional, Union

from application.port_out.text_generator_port import TextGeneratorPort
from domain.value.generated_word import GeneratedWord
from domain.value.job_info import RunningJob
from domain.value.job_input import JobInput
from domain.value.running_state import RunningState
from fyp23_model.sample import SampledImage, load_character_data, run_sample


class FontGenerationApplication(TextGeneratorPort):
    __seed: Optional[int]
    __image_save_path: Optional[str] = None

    def __init__(self, seed: Optional[int], image_save_path: Optional[str]):
        self.__seed = seed
        self.__image_save_path = image_save_path

    async def __generation(
        self,
        job_input: JobInput,
        job_info: RunningJob,
        on_new_state: Callable[[RunningState], None],
        on_new_word_result: Callable[[GeneratedWord], None],
    ) -> Union[bool, str]:
        def on_new_result(sample_result: SampledImage):
            on_new_state(
                RunningState.generating(
                    current=sample_result.current, total=sample_result.total
                )
            )
            on_new_word_result(
                GeneratedWord(
                    word=sample_result.word,
                    image=(
                        sample_result.image.tobytes()
                        if sample_result.image is not None
                        else None
                    ),
                )
            )

        if job_input.input_text == "":
            return True

        style_image, character_data = load_character_data(
            characters=job_input.input_text,
        )
        run_sample(
            style_image=style_image,
            character_data=character_data,
            seed=self.__seed,
            img_save_path=self.__image_save_path,
            on_new_result=on_new_result,
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
