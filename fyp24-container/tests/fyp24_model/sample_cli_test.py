import os
import subprocess

import pytest
import torch
from PIL import Image, ImageChops

### Constants ###


TEST_OUTPUT_FOLDER = "test_outputs/fyp24_model"


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


def run_sample_cli(character: str):
    assert len(character) == 1, "Length of character must be 1"

    ckpt_dir = "fyp24_model/ckpt"
    style_image_path = "fyp24_model/lan.png"
    save_image_dir = TEST_OUTPUT_FOLDER
    ttf_path = "fyp24_model/ttf/SourceHanSerifTC-VF.ttf"
    device = "cuda:0" if torch.cuda.is_available() else "cpu"

    command = (
        f"python -m fyp24_model.sample "
        f"--seed 0 "
        f"--ckpt_dir {ckpt_dir} "
        f"--style_image_path {style_image_path} "
        f"--character_input "
        f"--content_character {character} "
        f"--save_image "
        f"--save_image_dir {save_image_dir} "
        f"--device {device} "
        f"--algorithm_type dpmsolver++ "
        f"--guidance_type classifier-free "
        f"--guidance_scale 7.5 "
        f"--method multistep "
        f"--ttf_path {ttf_path} "
    )

    result = subprocess.check_output(command, shell=True, text=True, encoding="utf-8")
    return result


### Tests ###


@pytest.mark.cli
@pytest.mark.slow
def test_sample_single_traditional_chinese_word():
    expected_output_image_path = f"{TEST_OUTPUT_FOLDER}/書.png"

    remove_existing_file(expected_output_image_path)

    result = run_sample_cli(character="書")

    assert (
        "Finish the sampling process" in result
    ), "Expected message not found in output: 'Finish the sampling process'"

    output_image = Image.open(expected_output_image_path)

    expected_image = Image.open("tests/fyp24_model/test_sample_single_result/書.png")

    assert images_are_equal(
        output_image, expected_image
    ), f"Output image does not match expected image."

    remove_existing_file(expected_output_image_path)


@pytest.mark.cli
@pytest.mark.slow
def test_sample_single_simplified_chinese_word():
    expected_output_image_path = f"{TEST_OUTPUT_FOLDER}/书.png"

    remove_existing_file(expected_output_image_path)

    result = run_sample_cli(character="书")

    assert (
        "Finish the sampling process" in result
    ), "Expected message not found in output: 'Finish the sampling process'"

    output_image = Image.open(expected_output_image_path)

    expected_image = Image.open("tests/fyp24_model/test_sample_single_result/书.png")

    assert images_are_equal(
        output_image, expected_image
    ), f"Output image does not match expected image."

    remove_existing_file(expected_output_image_path)


@pytest.mark.cli
@pytest.mark.slow
def test_sample_single_english_character():
    expected_output_image_path = f"{TEST_OUTPUT_FOLDER}/A.png"

    remove_existing_file(expected_output_image_path)

    result = run_sample_cli(character="A")

    assert (
        "Finish the sampling process" in result
    ), "Expected message not found in output: 'Finish the sampling process'"

    output_image = Image.open(expected_output_image_path)

    expected_image = Image.open("tests/fyp24_model/test_sample_single_result/A.png")

    assert images_are_equal(
        output_image, expected_image
    ), f"Output image does not match expected image."

    remove_existing_file(expected_output_image_path)


@pytest.mark.cli
@pytest.mark.slow
def test_sample_single_number():
    expected_output_image_path = f"{TEST_OUTPUT_FOLDER}/1.png"

    remove_existing_file(expected_output_image_path)

    result = run_sample_cli(character="1")

    assert (
        "Finish the sampling process" in result
    ), "Expected message not found in output: 'Finish the sampling process'"

    output_image = Image.open(expected_output_image_path)

    expected_image = Image.open("tests/fyp24_model/test_sample_single_result/1.png")

    assert images_are_equal(
        output_image, expected_image
    ), f"Output image does not match expected image."

    remove_existing_file(expected_output_image_path)
