from uuid import UUID
import pytest
import pytest_asyncio  # pytest-asyncio is needed for async tests
from datetime import datetime

from adapter.data_access.font_generation_application import FontGenerationApplication
from domain.value.job_input import JobInput
from domain.value.job_info import RunningJob
from domain.value.running_state import RunningState
from domain.value.image_data import ImageData
from domain.value.image_result import ImageResult


@pytest.fixture
def font_generation_application():
    return FontGenerationApplication()


async def generate_text(
    font_generation_application: FontGenerationApplication, input_text: str
):
    job_input = JobInput(input_text=input_text)
    job_info = RunningJob(
        job_id=UUID("12345678-1234-5678-1234-567812345678"),
        time_start_to_queue=datetime.now(),
        time_start_to_run=datetime.now(),
        running_state=RunningState.not_started(),
    )

    result_list: list[ImageResult] = []

    def on_new_state(state: RunningState):
        pass

    def on_new_word_result(image_result: ImageResult):
        result_list.append(image_result)

    task = font_generation_application.generate_text(
        job_input=job_input,
        job_info=job_info,
        on_new_state=on_new_state,
        on_new_word_result=on_new_word_result,
    )

    await task

    return result_list


@pytest.mark.asyncio
async def test_generate_empty_text(font_generation_application):
    result = await generate_text(font_generation_application, "")
    assert result == []


@pytest.mark.asyncio
async def test_generate_missing_word(font_generation_application):
    result = await generate_text(font_generation_application, " ")
    assert result == [ImageResult(word=" ", image_data=None)]


# @pytest.mark.asyncio
# async def test_generate_single_traditional_chinese_word(font_generation_application):
#     result = await generate_text(font_generation_application, "書")
#     assert result == [("书", None)]


# @pytest.mark.asyncio
# async def test_generate_single_simplified_chinese_word(font_generation_application):
#     result = await generate_text(font_generation_application, "书")
#     assert result == [("书", None)]


# @pytest.mark.asyncio
# async def test_generate_single_english_character(font_generation_application):
#     result = await generate_text(font_generation_application, "A")
#     assert result == [("A", None)]


# @pytest.mark.asyncio
# async def test_generate_mixed_text(font_generation_application):
#     result = await generate_text(font_generation_application, "書书 A")
#     assert result == [("書", None), ("书", None), (" ", None), ("A", None)]
