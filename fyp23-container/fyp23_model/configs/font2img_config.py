import os
from typing import Optional

from pydantic import BaseModel, ConfigDict


def get_file_path(filename: str):
    """Get the absolute path of the file located in the root directory of the font model project.

    Context: This file is located in the `configs/` directory, which is one level above the root.
    """
    current_script_directory = os.path.dirname(__file__)
    root_directory = os.path.dirname(current_script_directory)
    return os.path.join(root_directory, filename)


class DefaultArguments(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    ttf_path: str = get_file_path("ttf_folder/PMingLiU.ttf")
    characters: Optional[str] = None
    text_path: Optional[str] = None
    save_path: str = get_file_path("content_folder")
    img_size: int = 80
    char_size: int = 60


font2img_default_args = DefaultArguments()


def add_font2img_arguments(parser):
    parser.add_argument(
        "--ttf_path",
        type=str,
        default=font2img_default_args.ttf_path,
        help="ttf directory",
    )
    parser.add_argument(
        "--characters",
        type=str,
        default=font2img_default_args.characters,
        help="characters; if not provided, will read from text_path",
    )
    parser.add_argument(
        "--text_path",
        type=str,
        default=font2img_default_args.text_path,
        help="text file containing characters; used if characters is not provided",
    )
    parser.add_argument(
        "--save_path",
        type=str,
        default=font2img_default_args.save_path,
        help="images directory",
    )
    parser.add_argument(
        "--img_size",
        type=int,
        default=font2img_default_args.img_size,
        help="The size of generated images",
    )
    parser.add_argument(
        "--char_size",
        type=int,
        default=font2img_default_args.char_size,
        help="The size of generated characters",
    )
