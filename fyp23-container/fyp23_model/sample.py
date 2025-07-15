import argparse
import os
import random
import shutil
from typing import Callable, Optional

import numpy as np
import torch as th
import torch.distributed as dist
import yaml
from attrdict import AttrDict
from PIL import Image

from fyp23_model.configs.font2img_config import (
    add_font2img_arguments,
    font2img_default_args,
)
from fyp23_model.configs.sample_config import (
    add_sample_arguments,
    create_sample_cfg,
    sample_default_args,
)
from fyp23_model.font2img import create_character_images_from_font
from fyp23_model.utils import dist_util, logger
from fyp23_model.utils.script_util import (
    args_to_dict,
    create_model_and_diffusion,
    model_and_diffusion_defaults,
)


class CharacterData:
    content_text: str
    content_images: list[Optional[Image.Image]]
    __length: int

    def __init__(self, content_text: str, content_images: list[Optional[Image.Image]]):
        assert len(content_text) == len(
            content_images
        ), "The length of content_text and content_images must be the same."
        self.content_text = content_text
        self.content_images = content_images
        self.__length = len(content_text)

    def __len__(self):
        return self.__length


class SampledImage:
    word: str
    image: Optional[Image.Image]
    current: int
    total: int

    def __init__(
        self, word: str, image: Optional[Image.Image], current: int, total: int
    ):
        assert (
            len(word) == 1
        ), "SampleResult should only contain a single character or word."
        self.word = word
        self.image = image
        self.current = current
        self.total = total


def img_pre_pros(img_path: Image.Image, image_size: tuple[int, int]) -> np.ndarray:
    pil_image = img_path.resize((image_size, image_size))
    pil_image.load()
    pil_image = pil_image.convert("RGB")
    arr = np.array(pil_image)
    arr = arr.astype(np.float32) / 127.5 - 1
    return np.transpose(arr, [2, 0, 1])


def main():
    parser = argparse.ArgumentParser()

    add_sample_arguments(parser)

    add_font2img_arguments(parser)

    parser = parser.parse_args()

    # read sample arguments
    seed = parser.seed
    cfg_path = parser.cfg_path
    model_path = parser.model_path
    sty_img_path = parser.sty_img_path
    con_folder_path = parser.con_folder_path
    gen_text_stroke_path = parser.gen_text_stroke_path
    total_txt_file = parser.total_txt_file
    img_save_path = parser.img_save_path
    ttf_path = parser.ttf_path
    classifier_free = parser.classifier_free
    cont_gudiance_scale = parser.cont_scale
    sk_gudiance_scale = parser.sk_scale

    # read font2img arguments
    ttf_path = parser.ttf_path
    characters = parser.characters
    text_path = parser.text_path
    img_size = parser.img_size
    char_size = parser.char_size

    # load data
    style_image, character_data = load_character_data(
        sty_img_path=sty_img_path,
        con_folder_path=con_folder_path,
        text_path=text_path,
        characters=characters,
        ttf_path=ttf_path,
        img_size=img_size,
        char_size=char_size,
    )

    # run sampling
    run_sample(
        seed=seed,
        style_image=style_image,
        character_data=character_data,
        cfg_path=cfg_path,
        model_path=model_path,
        gen_text_stroke_path=gen_text_stroke_path,
        total_txt_file=total_txt_file,
        img_save_path=img_save_path,
        classifier_free=classifier_free,
        cont_gudiance_scale=cont_gudiance_scale,
        sk_gudiance_scale=sk_gudiance_scale,
    )


def load_character_data(
    sty_img_path: str = sample_default_args.sty_img_path,
    con_folder_path: Optional[str] = sample_default_args.con_folder_path,
    text_path: Optional[str] = font2img_default_args.text_path,
    characters: Optional[str] = font2img_default_args.characters,
    ttf_path: str = font2img_default_args.ttf_path,
    img_size: int = font2img_default_args.img_size,
    char_size: int = font2img_default_args.char_size,
) -> tuple[Image.Image, CharacterData]:

    def load_from_characters(
        characters: str, font_path: str, img_size: int, char_size: int
    ) -> CharacterData:
        results, _, _ = create_character_images_from_font(
            characters=characters,
            font_path=font_path,
            img_size=img_size,
            char_size=char_size,
        )
        content_images = [result.image for result in results]

        return CharacterData(
            content_text=characters,
            content_images=content_images,
        )

    def load_from_con_folder_path(
        con_folder_path: str,
    ) -> CharacterData:
        # get words to be generated
        content_text = ""
        content_images = []
        for file in os.listdir(con_folder_path):
            file_name, file_extension = os.path.splitext(file)
            if file_extension == ".png":
                content_text += file_name[-1]
                content_images.append(Image.open(os.path.join(con_folder_path, file)))

        return CharacterData(
            content_text=content_text,
            content_images=content_images,
        )

    style_image = Image.open(sty_img_path)

    assert (
        characters is not None or text_path is None or con_folder_path is not None
    ), "Either characters, text_path, or con_folder_path must be provided."

    if characters is not None:
        character_data = load_from_characters(
            characters=characters,
            font_path=ttf_path,
            img_size=img_size,
            char_size=char_size,
        )
    elif text_path is not None:
        with open(text_path, "r", encoding="utf-8") as f:
            text = f.read().strip()
        character_data = load_from_characters(
            characters=text, font_path=ttf_path, img_size=img_size, char_size=char_size
        )
    else:
        assert con_folder_path is not None
        character_data = load_from_con_folder_path(con_folder_path)

    return style_image, character_data


def run_sample(
    style_image: Image.Image,
    character_data: CharacterData,
    seed: Optional[int] = sample_default_args.seed,
    cfg_path: str = sample_default_args.cfg_path,
    model_path: str = sample_default_args.model_path,
    gen_text_stroke_path: Optional[str] = sample_default_args.gen_text_stroke_path,
    total_txt_file: str = sample_default_args.total_txt_file,
    img_save_path: Optional[str] = sample_default_args.img_save_path,
    classifier_free: bool = sample_default_args.classifier_free,
    cont_gudiance_scale: float = sample_default_args.cont_scale,
    sk_gudiance_scale: float = sample_default_args.sk_scale,
    on_new_result: Callable[[SampledImage], None] = lambda _: None,
):
    # set up seed
    if seed is None:
        seed = random.randint(0, 2**32 - 1)
    th.manual_seed(seed)
    if th.cuda.is_available():
        th.cuda.manual_seed_all(seed)

    # set up cfg
    with open(cfg_path, "r", encoding="utf-8") as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    cfg = AttrDict(create_sample_cfg(cfg))

    # preprocess style image
    style_image = img_pre_pros(style_image, cfg.image_size)

    # preprocess content images
    content_images = [
        (
            img_pre_pros(content_image, cfg.image_size)
            if content_image is not None
            else None
        )
        for content_image in character_data.content_images
    ]

    # characters
    content_text = character_data.content_text

    # set up save directory
    if img_save_path is not None:
        # if os.path.exists(img_save_path):
        #     # remove the directory if it exists
        #     shutil.rmtree(img_save_path)

        # create the directory
        os.makedirs(img_save_path, exist_ok=True)
        os.chmod(img_save_path, 0o777)

    # set up dictionary for trained words
    char2idx = {}
    char_not_in_list = []
    with open(total_txt_file, "r", encoding="utf-8") as f:
        chars = f.readlines()
        for char in content_text:
            if char not in chars[0]:
                chars[0] += char
                char_not_in_list.append(char)
        for idx, char in enumerate(chars[0]):
            char2idx[char] = idx
        f.close()

    # get index of words to be generated
    char_idx = []
    for char in content_text:
        char_idx.append(char2idx[char])

    # set up distributed training
    dist_util.setup_dist()

    # create UNet model and diffusion
    logger.log("creating model and diffusion...")
    model, diffusion = create_model_and_diffusion(
        **args_to_dict(cfg, model_and_diffusion_defaults().keys())
    )

    # load model
    model.load_state_dict(dist_util.load_state_dict(model_path, map_location="cpu"))
    model.to(dist_util.dev())
    if cfg.use_fp16:
        model.convert_to_fp16()
    model.eval()
    logger.log("sampling...")
    noise = None

    all_images = []
    all_labels = []

    # for each batch
    # while len(all_images) * cfg.batch_size < cfg.num_samples:
    ch_idx = 0
    for batch_num, (char, content_image) in enumerate(
        zip(content_text, content_images)
    ):
        if content_image is None:
            on_new_result(
                SampledImage(
                    word=char,
                    image=None,
                    current=batch_num,
                    total=len(content_text),
                )
            )
            logger.log(f"Content image for character '{char}' is None, skipping.")
            continue

        model_kwargs = {}

        # process input content image
        con_img = th.tensor(
            content_image,
            requires_grad=False,
            device=dist_util.dev(),
        ).repeat(cfg.batch_size, 1, 1, 1)
        # con_feat = model.con_encoder(con_img)
        # model_kwargs["y"] = con_feat

        # process target style image
        sty_img = th.tensor(
            style_image,
            requires_grad=False,
            device=dist_util.dev(),
        ).repeat(cfg.batch_size, 1, 1, 1)
        sty_feat = model.sty_encoder(sty_img)
        model_kwargs["sty"] = sty_feat
        model_kwargs["cont"] = con_img

        # process input characters
        classes = th.tensor(
            [i for i in char_idx[ch_idx : ch_idx + cfg.batch_size]],
            device=dist_util.dev(),
        )
        ch_idx += cfg.batch_size

        model_kwargs["mask_y"] = th.zeros([cfg.batch_size], dtype=th.bool).to(
            dist_util.dev()
        )

        def model_fn(x_t, ts, **model_kwargs):
            model_output = model(x_t, ts, **model_kwargs)
            return model_output

        sample_fn = (
            diffusion.p_sample_loop if not cfg.use_ddim else diffusion.ddim_sample_loop
        )
        sample = sample_fn(
            model_fn,
            (cfg.batch_size, 3, cfg.image_size, cfg.image_size),
            # con_img = con_img,
            clip_denoised=cfg.clip_denoised,
            model_kwargs=model_kwargs,
            device=dist_util.dev(),
            noise=noise,
        )

        sample = ((sample + 1) * 127.5).clamp(0, 255).to(th.uint8)
        sample = sample.permute(0, 2, 3, 1)
        sample = sample.contiguous()

        gathered_samples = [th.zeros_like(sample) for _ in range(dist.get_world_size())]
        dist.all_gather(gathered_samples, sample)
        all_images.extend([sample.cpu().numpy() for sample in gathered_samples])

        gathered_labels = [th.zeros_like(classes) for _ in range(dist.get_world_size())]
        dist.all_gather(gathered_labels, classes)
        all_labels.extend([labels.cpu().numpy() for labels in gathered_labels])

        for sample_idx, sample in enumerate(gathered_samples):
            img_sample = sample[0].cpu().numpy()
            img = Image.fromarray(img_sample).convert("RGB")

            # report result to callback
            on_new_result(
                SampledImage(
                    word=char,
                    image=img,
                    current=batch_num,
                    total=len(content_text),
                )
            )

            # handle image saving
            if img_save_path is not None:
                seq_name = "" if sample_idx == 0 else f"_{sample_idx}"
                # img_name = "%05d%s.png" % (batch_num, seq_name)
                img_name = f"{char}{seq_name}.png"
                # img = remove_background(img)
                img.save(os.path.join(img_save_path, img_name))
                os.chmod(os.path.join(img_save_path, img_name), 0o777)

        total_samples_so_far = len(all_images) * cfg.batch_size
        logger.log(f"created {total_samples_so_far} samples so far")

    if dist.get_rank() == 0 and img_save_path is not None:
        if len(all_images) > 0 and len(all_labels) > 0:
            image_array = np.concatenate(all_images, axis=0)
            image_array = image_array[: cfg.num_samples]
            image_list = [
                Image.fromarray(img_sample).convert("RGB") for img_sample in image_array
            ]
            label_array = np.concatenate(all_labels, axis=0)
            label_array = label_array[: cfg.num_samples]
            # char2idx.keys()[char2idx.values().index(label)]

            # do something with image_list and label_array if needed

    dist.barrier()

    logger.log("sampling complete")


def remove_background(img: Image.Image):
    if img.mode != "RGBA":
        img = img.convert("RGBA")

    threshold = 200  # Adjust this value according to your image

    width, height = img.size
    pixels = img.load()

    for x in range(width):
        for y in range(height):
            r, g, b, a = pixels[x, y]

            if r > threshold or g > threshold or b > threshold:
                pixels[x, y] = (r, g, b, 0)  # Set the pixel to transparent

                # if a != 0:
                # pixels[x, y] = (0, 0, 0, a)

    return img


if __name__ == "__main__":
    main()
