import os
import subprocess

import pytest
from PIL import Image, ImageChops

### Constants ###


TEST_OUTPUT_FOLDER = "test_outputs/fyp23_model"


### Fixtures ###


@pytest.fixture(autouse=True)
def setup_output_folder():
    os.makedirs("./test_outputs", exist_ok=True)
    os.chmod("./test_outputs", 0o777)


### Helper Functions ###


def remove_existing_file(image_save_path):
    if os.path.isfile(image_save_path):
        os.remove(image_save_path)


def images_are_equal(image1: Image.Image, image2: Image.Image) -> bool:
    difference = ImageChops.difference(image1.convert("RGB"), image2.convert("RGB"))
    is_equal = difference.getbbox() is None
    return is_equal


def run_sample_cli(text: str):
    ttf_path = "fyp23_model/ttf_folder/PMingLiU.ttf"
    cfg_path = "fyp23_model/cfg/test_cfg.yaml"
    model_path = "fyp23_model/ckpt/ema_0.9999_446000.pt"
    sty_img_path = "fyp23_model/lan.png"
    total_txt_file = "fyp23_model/wordlist.txt"
    img_save_path = TEST_OUTPUT_FOLDER

    command = (
        f"python -m fyp23_model.sample "
        f"--seed 0 "
        f'--ttf_path "{ttf_path}" '
        f'--characters "{text}" '
        f'--cfg_path "{cfg_path}" '
        f'--model_path "{model_path}" '
        f'--sty_img_path "{sty_img_path}" '
        f'--total_txt_file "{total_txt_file}" '
        f'--img_save_path "{img_save_path}" '
    )

    result = subprocess.check_output(command, shell=True, text=True, encoding="utf-8")
    return result


### Tests ###


@pytest.mark.cli
@pytest.mark.slow
def test_sample_empty_text():
    result = run_sample_cli(text="")

    assert (
        "sampling complete" in result
    ), "Expected message not found in output: 'sampling complete'"


@pytest.mark.cli
@pytest.mark.slow
def test_sample_missing_character():
    result = run_sample_cli(text=" ")

    assert (
        "sampling complete" in result
    ), "Expected message not found in output: 'sampling complete'"


@pytest.mark.cli
@pytest.mark.slow
def test_sample_mixed_text():
    expected_output_image_path_0 = f"{TEST_OUTPUT_FOLDER}/書.png"
    expected_output_image_path_1 = f"{TEST_OUTPUT_FOLDER}/书.png"
    expected_output_image_path_3 = f"{TEST_OUTPUT_FOLDER}/A.png"
    expected_output_image_path_4 = f"{TEST_OUTPUT_FOLDER}/1.png"

    remove_existing_file(expected_output_image_path_0)
    remove_existing_file(expected_output_image_path_1)
    remove_existing_file(expected_output_image_path_3)
    remove_existing_file(expected_output_image_path_4)

    expected_image_0 = Image.open("tests/fyp23_model/test_sample_mixed_result/書.png")
    expected_image_1 = Image.open("tests/fyp23_model/test_sample_mixed_result/书.png")
    expected_image_3 = Image.open("tests/fyp23_model/test_sample_mixed_result/A.png")
    expected_image_4 = Image.open("tests/fyp23_model/test_sample_mixed_result/1.png")

    result = run_sample_cli(text="書书 A1")

    assert (
        "sampling complete" in result
    ), "Expected message not found in output: 'sampling complete'"

    output_image_0 = Image.open(expected_output_image_path_0)
    output_image_1 = Image.open(expected_output_image_path_1)
    output_image_3 = Image.open(expected_output_image_path_3)
    output_image_4 = Image.open(expected_output_image_path_4)

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

    remove_existing_file(expected_output_image_path_0)
    remove_existing_file(expected_output_image_path_1)
    remove_existing_file(expected_output_image_path_3)
    remove_existing_file(expected_output_image_path_4)
