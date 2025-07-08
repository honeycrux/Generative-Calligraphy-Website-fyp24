from abc import ABC, abstractmethod
from asyncio import Task
from typing import Callable, Union

from domain.value.generation_result import GenerationResult
from domain.value.job_info import RunningJob
from domain.value.job_input import JobInput
from domain.value.running_state import RunningState


class FontGenerationApplicationPort(ABC):
    """
    Port for font generation application.
    """

    @abstractmethod
    def generate_font(
        self,
        job_input: JobInput,
        job_info: RunningJob,
        on_new_state: Callable[[RunningState], None],
    ) -> Task[Union[GenerationResult, str]]:
        """
        Generate a font with the specified name and size.

        :param font_name: The name of the font to generate.
        :param font_size: The size of the font to generate.
        :return: The path to the generated font file.
        """
        pass
