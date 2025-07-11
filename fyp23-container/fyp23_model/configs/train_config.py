import os

from pydantic import BaseModel, ConfigDict

from utils.script_util import model_and_diffusion_defaults


def get_file_path(filename: str):
    """Get the absolute path of the file located in the root directory of the font model project.

    Context: This file is located in the `configs/` directory, which is one level above the root.
    """
    current_script_directory = os.path.dirname(__file__)
    root_directory = os.path.dirname(current_script_directory)
    return os.path.join(root_directory, filename)


class DefaultArguments(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")

    cfg_path: str = get_file_path("cfg/train_cfg.yaml")


train_default_args = DefaultArguments()


def add_train_arguments(parser):
    parser.add_argument(
        "--cfg_path",
        type=str,
        default=train_default_args.cfg_path,
        help="config file path",
    )


# create configuration cfg from cfg.yaml
def create_train_cfg(cfg):
    defaults = dict(
        data_dir="",
        content_dir="",
        schedule_sampler="uniform",
        lr=1e-4,
        weight_decay=0.0,
        lr_anneal_steps=0,
        batch_size=1,
        microbatch=-1,
        ema_rate="0.9999",
        log_interval=250,
        save_interval=20000,
        resume_checkpoint="",
        use_fp16=False,
        fp16_scale_growth=1e-3,
        stroke_path=None,
        attention_resolutions="40, 20, 10",
    )
    defaults.update(model_and_diffusion_defaults())
    defaults.update(cfg)
    return defaults
