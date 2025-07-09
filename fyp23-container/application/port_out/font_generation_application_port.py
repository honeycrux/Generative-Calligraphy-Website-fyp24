from abc import ABC, abstractmethod
from asyncio import Task
from typing import Callable, Optional, Union

from domain.value.generation_result import GenerationResult
from domain.value.image_data import ImageData
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
        on_new_word_result: Callable[[str, Optional[ImageData]], None],
    ) -> Task[Union[bool, str]]:
        """
        Generate a font with the specified name and size.

        :param job_input: The input for the job.
        :param job_info: The information about the job.
        :param on_new_state: Callback for new state updates.
        :param on_new_word_result: Callback for new word results.
        :return: A task that resolves to a boolean indicating success or an error message.
        """
        pass
