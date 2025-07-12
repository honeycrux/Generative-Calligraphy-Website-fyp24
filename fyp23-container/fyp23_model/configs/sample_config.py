import os
from typing import Optional

from pydantic import BaseModel, ConfigDict

from fyp23_model.utils.script_util import model_and_diffusion_defaults


def get_file_path(filename: str):
    """Get the absolute path of the file located in the root directory of the font model project.

    Context: This file is located in the `configs/` directory, which is one level above the root.
    """
    current_script_directory = os.path.dirname(__file__)
    root_directory = os.path.dirname(current_script_directory)
    return os.path.join(root_directory, filename)


class DefaultArguments(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    seed: Optional[int] = None
    cfg_path: str = get_file_path("cfg/test_cfg.yaml")
    model_path: str = get_file_path("ckpt/ema_0.9999_446000.pt")
    sty_img_path: str = get_file_path("lan.png")
    con_folder_path: Optional[str] = None
    gen_text_stroke_path: Optional[str] = None  # (unused)
    total_txt_file: str = get_file_path("wordlist.txt")
    img_save_path: Optional[str] = None
    classifier_free: bool = False  # (unused)
    cont_scale: float = 3.0  # (unused)
    sk_scale: float = 3.0  # (unused)


sample_default_args = DefaultArguments()


def add_sample_arguments(parser):
    parser.add_argument(
        "--seed",
        type=int,
        default=sample_default_args.seed,
        help="random seed for reproducibility; if not provided, will use a random seed",
    )
    parser.add_argument(
        "--cfg_path",
        type=str,
        default=sample_default_args.cfg_path,
        help="config file path",
    )
    parser.add_argument(
        "--model_path",
        type=str,
        default=sample_default_args.model_path,
        help="path to the model checkpoint",
    )
    parser.add_argument(
        "--sty_img_path",
        type=str,
        default=sample_default_args.sty_img_path,
        help="path to the style image",
    )
    parser.add_argument(
        "--con_folder_path",
        type=str,
        default=sample_default_args.con_folder_path,
        help="path to the folder containing content images; will be used if characters/text_path is not provided",
    )
    parser.add_argument(
        "--gen_text_stroke_path",
        type=str,
        default=sample_default_args.gen_text_stroke_path,
        help="path to output the generated stroke information of the input characters",
    )
    parser.add_argument(
        "--total_txt_file",
        type=str,
        default=sample_default_args.total_txt_file,
        help="path to the file containing the stroke information of all known characters",
    )
    parser.add_argument(
        "--img_save_path",
        type=str,
        default=sample_default_args.img_save_path,
        help="path to save the generated images, if not provided, will not save images",
    )
    parser.add_argument(
        "--classifier_free",
        type=bool,
        default=sample_default_args.classifier_free,
    )
    parser.add_argument(
        "--cont_scale",
        type=float,
        default=sample_default_args.cont_scale,
    )
    parser.add_argument(
        "--sk_scale",
        type=float,
        default=sample_default_args.sk_scale,
    )


def create_sample_cfg(cfg):
    defaults = dict(
        clip_denoised=True,
        num_samples=100,
        batch_size=16,
        use_ddim=False,
        model_path="",
        cont_scale=1.0,
        sk_scale=1.0,
        sty_img_path="",
        # gen_text_stroke_path="", # add
        # stroke_path=None,
        attention_resolutions="40, 20, 10",
    )
    defaults.update(model_and_diffusion_defaults())
    defaults.update(cfg)
    return defaults
