import argparse
import os
import pathlib
from typing import Optional

import numpy as np
from fontTools.ttLib import TTFont
from PIL import Image, ImageDraw, ImageFont

from fyp23_model.configs.font2img_config import (
    add_font2img_arguments,
    font2img_default_args,
)


class CharacterResult:
    character: str
    image: Optional[Image.Image]

    def __init__(self, character: str, image: Optional[Image.Image] = None):
        self.character = character
        self.image = image


def get_char_list_from_ttf(font_file):
    f_obj = TTFont(font_file)
    m_dict = f_obj.getBestCmap()

    unicode_list = []
    for key, uni in m_dict.items():
        unicode_list.append(key)

    char_list = [chr(ch_unicode) for ch_unicode in unicode_list]
    return char_list


def draw_single_char(ch, font, canvas_size, x_offset, y_offset):
    img = Image.new("RGB", (canvas_size, canvas_size), (255, 255, 255))
    draw = ImageDraw.Draw(img)
    draw.text((x_offset, y_offset), ch, (0, 0, 0), font=font)
    return img


def draw_example(ch, src_font, canvas_size, x_offset, y_offset):
    src_img = draw_single_char(ch, src_font, canvas_size, x_offset, y_offset)
    example_img = Image.new("RGB", (canvas_size, canvas_size), (255, 255, 255))
    example_img.paste(src_img, (0, 0))
    return example_img


def main():
    parser = argparse.ArgumentParser(description="Obtaining characters from .ttf")
    add_font2img_arguments(parser)
    args = parser.parse_args()

    ttf_path = args.ttf_path
    characters = args.characters
    text_path = args.text_path
    save_path = args.save_path
    img_size = args.img_size
    char_size = args.char_size

    run_font2img(
        ttf_path=ttf_path,
        characters=characters,
        text_path=text_path,
        save_path=save_path,
        img_size=img_size,
        char_size=char_size,
    )


def run_font2img(
    ttf_path: str,
    characters: Optional[str],
    text_path: str,
    save_path: str,
    img_size: int = font2img_default_args.img_size,
    char_size: int = font2img_default_args.char_size,
):
    # if os.path.exists(save_path):
    #     shutil.rmtree(save_path)

    if not os.path.exists(save_path):
        os.mkdir(save_path)
    os.chmod(save_path, 0o777)

    if characters is None:
        with open(text_path, "r", encoding="utf-8") as f:
            characters = f.read().strip()

    print("Font2img received input:", characters)

    ttf_location = pathlib.Path(ttf_path)

    single_font_mode = ttf_location.is_file()

    if single_font_mode:
        generate_with_single_font_mode(
            characters=characters,
            save_path=save_path,
            img_size=img_size,
            char_size=char_size,
            ttf_location=ttf_location,
        )

    if not single_font_mode:
        generate_with_multi_font_mode(
            characters=characters,
            save_path=save_path,
            img_size=img_size,
            char_size=char_size,
            ttf_location=ttf_location,
        )


def generate_with_multi_font_mode(
    characters: str,
    save_path: str,
    ttf_location: pathlib.Path,
    img_size: int,
    char_size: int,
) -> None:
    font_file_paths = list(ttf_location.glob("*.*"))  # *.ttf TTF
    font_file_paths = [path.as_posix() for path in font_file_paths]
    font_file_count = len(font_file_paths)
    if font_file_count == 0:
        raise ValueError(f"No .ttf file found in the directory {ttf_location}.")

    if not os.path.exists(save_path):
        os.mkdir(save_path)

    for idx, font_path in enumerate(font_file_paths):
        print("{}/{} ".format(idx + 1, font_file_count), font_path)

        results, img_cnt, filter_cnt = create_character_images_from_font(
            img_size=img_size,
            char_size=char_size,
            characters=characters,
            font_path=font_path,
        )

        # Create a subdirectory for each font
        font_name = font_path.split("/")[-1].split(".")[0]
        save_directory = os.path.join(save_path, font_name)
        if not os.path.exists(save_directory):
            os.mkdir(save_directory)
            os.chmod(save_directory, 0o777)

        for cnt, result in enumerate(results):
            if result.image is None:
                continue
            result.image.save(os.path.join(save_directory, result.character + ".png"))
            # result.image.save(os.path.join(save_directory, "%05d.png" % (cnt)))
            os.chmod(os.path.join(save_directory, result.character + ".png"), 0o777)

        print(img_cnt, "characters are generated as images")
        print(filter_cnt, "characters are missing in this font")


def generate_with_single_font_mode(
    characters: str,
    save_path: str,
    ttf_location: pathlib.Path,
    img_size: int,
    char_size: int,
) -> None:
    results, img_cnt, filter_cnt = create_character_images_from_font(
        img_size=img_size,
        char_size=char_size,
        characters=characters,
        font_path=str(ttf_location),
    )

    save_directory = save_path
    if not os.path.exists(save_directory):
        os.mkdir(save_directory)

    for cnt, result in enumerate(results):
        if result.image is None:
            continue
        result.image.save(os.path.join(save_directory, result.character + ".png"))
        # result.image.save(os.path.join(save_directory, "%05d.png" % (cnt)))
        os.chmod(os.path.join(save_directory, result.character + ".png"), 0o777)

    print(img_cnt, "characters are generated as images")
    print(filter_cnt, "characters are missing in this font")


def create_character_images_from_font(
    characters: str,
    font_path: str,
    img_size: int = font2img_default_args.img_size,
    char_size: int = font2img_default_args.char_size,
) -> tuple[list[CharacterResult], int, int]:
    src_font = ImageFont.truetype(font_path, size=char_size)
    # chars = get_char_list_from_ttf(item)
    img_cnt = 0
    filter_cnt = 0
    results: list[CharacterResult] = []
    for cnt, character in enumerate(characters):
        img = draw_example(
            character,
            src_font,
            img_size,
            (img_size - char_size) / 2,
            (img_size - char_size) / 2,
        )
        not_successful = img_size * img_size * 3 - np.sum(np.array(img) / 255.0) < 100
        if not_successful:
            filter_cnt += 1
            results.append(CharacterResult(character=character, image=None))
        else:
            img_cnt += 1
            results.append(CharacterResult(character=character, image=img))

    return results, img_cnt, filter_cnt


if __name__ == "__main__":
    main()
