from abc import ABC, abstractmethod
from asyncio import Task
from typing import Callable, Optional, Union

from domain.value.generated_word import GeneratedWord
from domain.value.job_info import RunningJob
from domain.value.job_input import JobInput
from domain.value.running_state import RunningState


class TextGeneratorPort(ABC):
    """
    Port for text generation.
    This port defines the interface for the application that generates text.
    """

    @abstractmethod
    def generate_text(
        self,
        job_input: JobInput,
        job_info: RunningJob,
        on_new_state: Callable[[RunningState], None],
        on_new_word_result: Callable[[GeneratedWord], None],
    ) -> Task[Union[bool, str]]:
        """
        Generate text based on the job input.

        :param job_input: The input for the job.
        :param job_info: The information about the job.
        :param on_new_state: Callback for new state updates.
        :param on_new_word_result: Callback for new word results.
        :return: A task that resolves to a boolean indicating success or an error message.
        """
        pass
