from datetime import datetime
from uuid import UUID

import pytest
import pytest_asyncio  # pytest-asyncio is needed for async tests
from PIL import Image

from adapter.data_access.font_generation_application import FontGenerationApplication
from domain.value.generated_word import GeneratedWord
from domain.value.job_info import RunningJob
from domain.value.job_input import JobInput
from domain.value.running_state import RunningState

### Fixtures ###


@pytest.fixture
def font_generation_application():
    font_app = FontGenerationApplication(seed=0, image_save_path=None)

    # To also save images to `fyp23-container/test_outputs`
    # (useful for generating true images or finding out issues),
    # you can set the image save path:
    # font_app = FontGenerationApplication(seed=0, image_save_path="./test_outputs")

    return font_app


### Helper Function ###


async def generate_text(
    font_generation_application: FontGenerationApplication, input_text: str
):
    job_input = JobInput(input_text=input_text)
    job_info = RunningJob(
        time_start_to_queue=datetime.now(),
        time_start_to_run=datetime.now(),
        running_state=RunningState.not_started(),
    )

    result_list: list[GeneratedWord] = []

    def on_new_state(state: RunningState):
        pass

    def on_new_word_result(generated_word: GeneratedWord):
        result_list.append(generated_word)

    task = font_generation_application.generate_text(
        job_input=job_input,
        job_info=job_info,
        on_new_state=on_new_state,
        on_new_word_result=on_new_word_result,
    )

    await task

    return result_list


### Tests ###


@pytest.mark.slow
@pytest.mark.asyncio
async def test_generate_empty_text(font_generation_application):
    result = await generate_text(font_generation_application, "")

    assert result == []


@pytest.mark.slow
@pytest.mark.asyncio
async def test_generate_missing_character(font_generation_application):
    result = await generate_text(font_generation_application, " ")

    assert result == [GeneratedWord.from_image(word=" ", image=None)]


@pytest.mark.slow
@pytest.mark.asyncio
async def test_generate_single_traditional_chinese_word(font_generation_application):
    expected_image = Image.open(
        "./tests/adapter/data_access/test_generate_single_result/書.png"
    )

    result = await generate_text(font_generation_application, "書")

    assert result == [GeneratedWord.from_image("書", expected_image)]


@pytest.mark.slow
@pytest.mark.asyncio
async def test_generate_single_simplified_chinese_word(font_generation_application):
    expected_image = Image.open(
        "./tests/adapter/data_access/test_generate_single_result/书.png"
    )

    result = await generate_text(font_generation_application, "书")

    assert result == [GeneratedWord.from_image("书", expected_image)]


@pytest.mark.slow
@pytest.mark.asyncio
async def test_generate_single_english_character(font_generation_application):
    expected_image = Image.open(
        "./tests/adapter/data_access/test_generate_single_result/A.png"
    )

    result = await generate_text(font_generation_application, "A")

    assert result == [GeneratedWord.from_image("A", expected_image)]


@pytest.mark.slow
@pytest.mark.asyncio
async def test_generate_single_number(font_generation_application):
    expected_image = Image.open(
        "./tests/adapter/data_access/test_generate_single_result/1.png"
    )

    result = await generate_text(font_generation_application, "1")

    assert result == [GeneratedWord.from_image("1", expected_image)]


@pytest.mark.slow
@pytest.mark.asyncio
async def test_generate_mixed_text(font_generation_application):
    expected_image_0 = Image.open(
        "./tests/adapter/data_access/test_generate_mixed_result/書.png"
    )
    expected_image_1 = Image.open(
        "./tests/adapter/data_access/test_generate_mixed_result/书.png"
    )
    expected_image_3 = Image.open(
        "./tests/adapter/data_access/test_generate_mixed_result/A.png"
    )
    expected_image_4 = Image.open(
        "./tests/adapter/data_access/test_generate_mixed_result/1.png"
    )

    result = await generate_text(font_generation_application, "書书 A1")

    assert result == [
        GeneratedWord.from_image("書", expected_image_0),
        GeneratedWord.from_image("书", expected_image_1),
        GeneratedWord.from_image(" ", None),
        GeneratedWord.from_image("A", expected_image_3),
        GeneratedWord.from_image("1", expected_image_4),
    ]
