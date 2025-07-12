import argparse

import torch as th
from attrdict import AttrDict
import yaml

from utils import dist_util, logger
from utils.word_imagesets import load_data
from utils.resample import create_named_schedule_sampler
from utils.script_util import (
    model_and_diffusion_defaults,
    args_to_dict,
    create_model_and_diffusion,
)
from utils.train_util import TrainLoop
from configs.train_config import add_train_arguments, create_train_cfg


def main():

    # read input command
    parser = argparse.ArgumentParser()
    add_train_arguments(parser)
    parser = parser.parse_args()

    # set up configuration cfg
    with open(parser.cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    cfg = AttrDict(create_train_cfg(cfg))
    train_step = cfg.train_step
    total_train_step = cfg.total_train_step
    sty_encoder_path = cfg.sty_encoder_path
    classifier_free = cfg.classifier_free
    cfg.__delattr__("train_step")
    cfg.__delattr__("total_train_step")
    cfg.__delattr__("sty_encoder_path")
    cfg.__delattr__("classifier_free")

    # set up pytorch distributed training
    dist_util.setup_dist()

    # set up model save directory
    model_save_dir = cfg.model_save_dir
    if not os.path.exists(model_save_dir):
        os.mkdir(model_save_dir)

    # set up logger
    logger.configure(dir=model_save_dir, format_strs=["stdout", "log", "csv"])

    # create UNet model and diffusion
    logger.log("creating model and diffusion...")
    model, diffusion = create_model_and_diffusion(
        **args_to_dict(cfg, model_and_diffusion_defaults().keys())
    )
    model.to(dist_util.dev())
    schedule_sampler = create_named_schedule_sampler(cfg.schedule_sampler, diffusion)

    # load style encoder (new training, no checkpoint)
    if not cfg.resume_checkpoint:
        logger.log("loading pre-trained model...")

        # load style encoder parameter
        checkpoint = th.load(sty_encoder_path, map_location="cpu")
        tmp_dict = {}
        for k, v in checkpoint.items():
            if k in model.sty_encoder.state_dict():
                tmp_dict[k] = v
        model.sty_encoder.load_state_dict(tmp_dict)

        # fine-tuning
        if classifier_free:
            raise ValueError(
                f"required conditional trained model, please fill in the model path in 'resume_checkpoint'"
            )

    # froze style encoder
    for p in model.sty_encoder.parameters():
        p.requires_grad = False

    # # load content encoder??
    # # froze content encoder??
    # for p in model.con_encoder.parameters():
    #     p.requires_grad = False

    # load data
    logger.log("creating data loader...")
    data = load_data(
        data_dir=cfg.data_dir,
        content_dir=cfg.content_dir,
        batch_size=cfg.batch_size,
        image_size=cfg.image_size,
        stroke_path=cfg.stroke_path,
        classifier_free=classifier_free,
    )

    """# for content encoder
    data = load_data(
        data_dir=cfg.content_dir,
        batch_size=cfg.batch_size,
        image_size=cfg.image_size,
        stroke_path=cfg.stroke_path,
        classifier_free=classifier_free,
    )"""

    # train
    logger.log("training...")
    TrainLoop(
        model=model,
        diffusion=diffusion,
        data=data,
        batch_size=cfg.batch_size,
        microbatch=cfg.microbatch,
        lr=cfg.lr,
        ema_rate=cfg.ema_rate,
        log_interval=cfg.log_interval,
        save_interval=cfg.save_interval,
        train_step=train_step,
        resume_checkpoint=cfg.resume_checkpoint,
        use_fp16=cfg.use_fp16,
        fp16_scale_growth=cfg.fp16_scale_growth,
        schedule_sampler=schedule_sampler,
        weight_decay=cfg.weight_decay,
        classifier_free=classifier_free,
        total_train_step=total_train_step,
    ).run_loop()


if __name__ == "__main__":
    import os

    main()
