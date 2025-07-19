import os
import subprocess

import pytest
from PIL import Image, ImageChops

### Constants ###


TEST_OUTPUT_FOLDER = "test_outputs/fyp23_model"


### Fixtures ###


@pytest.fixture(autouse=True)
def setup_output_folder():
    os.makedirs(TEST_OUTPUT_FOLDER, exist_ok=True)
    os.chmod("test_outputs", 0o777)
    os.chmod(TEST_OUTPUT_FOLDER, 0o777)


### Helper Functions ###


def remove_existing_file(image_save_path):
    if os.path.isfile(image_save_path):
        os.remove(image_save_path)


def images_are_equal(image1: Image.Image, image2: Image.Image) -> bool:
    difference = ImageChops.difference(image1.convert("RGB"), image2.convert("RGB"))
    is_equal = difference.getbbox() is None
    return is_equal


def run_font2img_cli(text: str):
    ttf_path = "fyp23_model/ttf_folder/PMingLiU.ttf"
    save_path = TEST_OUTPUT_FOLDER

    command = (
        f"python -m fyp23_model.font2img "
        f'--ttf_path "{ttf_path}" '
        f'--save_path "{save_path}" '
        f'--characters "{text}" '
    )

    result = subprocess.check_output(command, shell=True, text=True, encoding="utf-8")
    return result


### Tests ###


@pytest.mark.cli
def test_sample_empty_text():
    result = run_font2img_cli(text="")

    assert (
        "0 characters are missing in this font" in result
    ), "Expected message not found in output: '0 characters are missing in this font'"


@pytest.mark.cli
def test_prepare_missing_character():
    result = run_font2img_cli(text=" ")

    assert (
        "1 characters are missing in this font" in result
    ), "Expected message not found in output: '1 characters are missing in this font'"


@pytest.mark.cli
def test_prepare_single_traditional_chinese_word():
    expected_output_image_path = f"{TEST_OUTPUT_FOLDER}/書.png"
    remove_existing_file(expected_output_image_path)

    result = run_font2img_cli(text="書")

    assert (
        "0 characters are missing in this font" in result
    ), "Expected message not found in output: '0 characters are missing in this font'"

    output_image = Image.open(expected_output_image_path)

    expected_image = Image.open("tests/fyp23_model/test_font2img_result/書.png")

    assert images_are_equal(
        output_image, expected_image
    ), f"Output image does not match expected image."

    remove_existing_file(expected_output_image_path)


@pytest.mark.cli
def test_prepare_single_simplified_chinese_word():
    expected_output_image_path = f"{TEST_OUTPUT_FOLDER}/书.png"
    remove_existing_file(expected_output_image_path)

    result = run_font2img_cli(text="书")

    assert (
        "0 characters are missing in this font" in result
    ), "Expected message not found in output: '0 characters are missing in this font'"

    output_image = Image.open(expected_output_image_path)

    expected_image = Image.open("tests/fyp23_model/test_font2img_result/书.png")

    assert images_are_equal(
        output_image, expected_image
    ), f"Output image does not match expected image."

    remove_existing_file(expected_output_image_path)


@pytest.mark.cli
def test_prepare_single_english_character():
    expected_output_image_path = f"{TEST_OUTPUT_FOLDER}/A.png"
    remove_existing_file(expected_output_image_path)

    result = run_font2img_cli(text="A")

    assert (
        "0 characters are missing in this font" in result
    ), "Expected message not found in output: '0 characters are missing in this font'"

    output_image = Image.open(expected_output_image_path)

    expected_image = Image.open("tests/fyp23_model/test_font2img_result/A.png")

    assert images_are_equal(
        output_image, expected_image
    ), f"Output image does not match expected image."

    remove_existing_file(expected_output_image_path)


@pytest.mark.cli
def test_prepare_single_number():
    expected_output_image_path = f"{TEST_OUTPUT_FOLDER}/1.png"
    remove_existing_file(expected_output_image_path)

    result = run_font2img_cli(text="1")

    assert (
        "0 characters are missing in this font" in result
    ), "Expected message not found in output: '0 characters are missing in this font'"

    output_image = Image.open(expected_output_image_path)

    expected_image = Image.open("tests/fyp23_model/test_font2img_result/1.png")

    assert images_are_equal(
        output_image, expected_image
    ), f"Output image does not match expected image."

    remove_existing_file(expected_output_image_path)


@pytest.mark.cli
def text_prepare_mixed_text():
    expected_output_image_path_0 = f"{TEST_OUTPUT_FOLDER}/書.png"
    expected_output_image_path_1 = f"{TEST_OUTPUT_FOLDER}/书.png"
    expected_output_image_path_3 = f"{TEST_OUTPUT_FOLDER}/A.png"
    expected_output_image_path_4 = f"{TEST_OUTPUT_FOLDER}/1.png"

    remove_existing_file(expected_output_image_path_0)
    remove_existing_file(expected_output_image_path_1)
    remove_existing_file(expected_output_image_path_3)
    remove_existing_file(expected_output_image_path_4)

    result = run_font2img_cli(text="書书 A1")

    assert (
        "1 characters are missing in this font" in result
    ), "Expected message not found in output: '1 characters are missing in this font'"

    output_image_0 = Image.open(expected_output_image_path_0)
    output_image_1 = Image.open(expected_output_image_path_1)
    output_image_3 = Image.open(expected_output_image_path_3)
    output_image_4 = Image.open(expected_output_image_path_4)

    expected_image_0 = Image.open("tests/fyp23_model/test_font2img_result/書.png")
    expected_image_1 = Image.open("tests/fyp23_model/test_font2img_result/书.png")
    expected_image_3 = Image.open("tests/fyp23_model/test_font2img_result/A.png")
    expected_image_4 = Image.open("tests/fyp23_model/test_font2img_result/1.png")

    assert images_are_equal(
        output_image_0, expected_image_0
    ), f"Output image 0 does not match expected image."
    assert images_are_equal(
        output_image_1, expected_image_1
    ), f"Output image 1 does not match expected image."
    assert images_are_equal(
        output_image_3, expected_image_3
    ), f"Output image 3 does not match expected image."
    assert images_are_equal(
        output_image_4, expected_image_4
    ), f"Output image 4 does not match expected image."
