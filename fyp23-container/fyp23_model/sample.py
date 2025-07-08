import argparse
import os

import numpy as np
import torch as th
import torch.distributed as dist

from utils import dist_util, logger
from utils.script_util import (
    model_and_diffusion_defaults,
    args_to_dict,
    create_model_and_diffusion,
)
from PIL import Image
from attrdict import AttrDict
import yaml
import shutil


def img_pre_pros(img_path, image_size):
    pil_image = Image.open(img_path).resize((image_size, image_size))
    pil_image.load()
    pil_image = pil_image.convert("RGB")
    arr = np.array(pil_image)
    arr = arr.astype(np.float32) / 127.5 - 1
    return np.transpose(arr, [2, 0, 1])


def main():
    parser = argparse.ArgumentParser()

    # add arguments
    parser.add_argument('--cfg_path', type=str, default='./cfg/test_cfg.yaml',
                        help='config file path')
    parser.add_argument('--session_id', type=str, default='01',
                        help='session id for client') # (unused)
    parser.add_argument('--model_path', type=str, default='./ckpt/ema_0.9999_446000.pt',)
    parser.add_argument('--sty_img_path', type=str, default='./lan.png',)
    parser.add_argument('--con_folder_path', type=str, default='./content_folder',)
    parser.add_argument('--gen_text_stroke_path', type=str, default=None,) # (unused)
    parser.add_argument('--total_txt_file', type=str, default='./wordlist.txt',)
    parser.add_argument('--img_save_path', type=str, default='./result_web',)
    parser.add_argument('--classifier_free', type=bool, default=False,) # (unused)
    parser.add_argument('--cont_scale', type=float, default=3.0,) # (unused)
    parser.add_argument('--sk_scale', type=float, default=3.0,) # (unused)

    parser = parser.parse_args()

    # get arguments
    cfg_path = parser.cfg_path
    session_id = parser.session_id # (unused)
    model_path = parser.model_path
    sty_img_path = parser.sty_img_path
    con_folder_path = parser.con_folder_path
    gen_text_stroke_path = parser.gen_text_stroke_path # (unused)
    total_txt_file = parser.total_txt_file
    img_save_path = parser.img_save_path
    classifier_free = parser.classifier_free # (unused)
    cont_gudiance_scale = parser.cont_scale # (unused)
    sk_gudiance_scale = parser.sk_scale # (unused)

    # set up cfg
    with open(cfg_path, 'r', encoding='utf-8') as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    cfg = AttrDict(create_cfg(cfg))


    # set up distributed training
    dist_util.setup_dist()

    # save directory
    if not os.path.exists(img_save_path):
        os.mkdir(img_save_path)
    else:
        shutil.rmtree(img_save_path)
        os.mkdir(img_save_path)
    os.chmod(img_save_path, 0o777)

    # create UNet model and diffusion
    logger.log("creating model and diffusion...")
    model, diffusion = create_model_and_diffusion(
        **args_to_dict(cfg, model_and_diffusion_defaults().keys())
    )

    # load model
    model.load_state_dict(
        dist_util.load_state_dict(model_path, map_location="cpu")
    )
    model.to(dist_util.dev())
    if cfg.use_fp16:
        model.convert_to_fp16()
    model.eval()
    logger.log("sampling...")
    noise = None
    # get words to be generated
    gen_txt=[]
    for file in os.listdir(con_folder_path):
        file_name, file_extension = os.path.splitext(file)
        if file_extension == ".png":
            gen_txt.append(file_name[-1])

    # set up dictionary for trained words
    char2idx = {}
    char_not_in_list = []
    with open(total_txt_file, 'r', encoding='utf-8') as f:
        chars = f.readlines()
        for char in gen_txt:
            if char not in chars[0]:
                chars[0] += char
                char_not_in_list.append(char)
        for idx, char in enumerate(chars[0]):
            char2idx[char] = idx
        f.close()

    # get index of words to be generated
    char_idx = []
    for char in gen_txt:
        char_idx.append(char2idx[char])
    
    all_images = []
    all_labels = []

    stroke_dict = {}
    if gen_text_stroke_path is not None:
        with open(gen_text_stroke_path, 'r') as f:
            gen_text_stroke = f.readlines()
            for gen_strokes in gen_text_stroke:
                stroke_dict[gen_strokes[0]] = gen_strokes[1:]
        f.close()

    # for each batch
    # while len(all_images) * cfg.batch_size < cfg.num_samples:
    ch_idx = 0
    for char in gen_txt:

        model_kwargs = {}

        # logger.log("1...")
        # process input content image
        con_img = th.tensor(img_pre_pros(con_folder_path + "/" + char + ".png", cfg.image_size), requires_grad=False, device=dist_util.dev()).repeat(cfg.batch_size, 1, 1, 1)
        # con_feat = model.con_encoder(con_img)
        # model_kwargs["y"] = con_feat

        # logger.log("2...")
        # process target style image
        sty_img = th.tensor(img_pre_pros(sty_img_path, cfg.image_size), requires_grad=False, device=dist_util.dev()).repeat(cfg.batch_size, 1, 1, 1)
        sty_feat = model.sty_encoder(sty_img)
        model_kwargs["sty"] = sty_feat
        model_kwargs["cont"] = con_img

        # logger.log("3...")
        # process input characters
        classes = th.tensor([i for i in char_idx[ch_idx:ch_idx + cfg.batch_size]], device=dist_util.dev())
        ch_idx += cfg.batch_size

        # logger.log("4...")
        # read stroke information
        '''if cfg.stroke_path is not None:
            chars_stroke = th.empty([0, 32], dtype=th.float32)

            # read all stroke
            with open(cfg.stroke_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                # need to be in order????
                if gen_text_stroke_path == None:
                    for char in char_not_in_list:
                        lines.append(char + " 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0\n")
                else:
                    for chn in char_not_in_list:
                        lines.append(chn + stroke_dict[chn])
                for line in lines:
                    strokes = line.split(" ")[1:-1]
                    char_stroke = []
                    for stroke in strokes:
                        char_stroke.append(int(stroke))
                    while len(char_stroke) < 32:  # for korean
                        char_stroke.append(0)
                    assert len(char_stroke) == 32
                    chars_stroke = th.cat((chars_stroke, th.tensor(char_stroke).reshape([1, 32])), dim=0)
            f.close()

            # take needed info
            if classes >= 3000:
                stk = "0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0"
                stkth = th.tensor(stk)
                model_kwargs["stroke"] = stkth.to(dist_util.dev())
            else:
            device = dist_util.dev()
            chars_stroke = chars_stroke.to(device)
            model_kwargs["stroke"] = chars_stroke[classes].to(device)
            #model_kwargs["stroke"] = chars_stroke[classes].to(dist_util.dev())'''

        '''if classifier_free:
            if cfg.stroke_path is not None:
                model_kwargs["mask_y"] = th.cat([th.zeros([cfg.batch_size], dtype=th.bool), th.ones([cfg.batch_size * 2], dtype=th.bool)]).to(dist_util.dev())
                model_kwargs["y"] = model_kwargs["y"].repeat(3)
                model_kwargs["mask_stroke"] = th.cat(
                    [th.ones([cfg.batch_size], dtype=th.bool),th.zeros([cfg.batch_size], dtype=th.bool), th.ones([cfg.batch_size], dtype=th.bool)]).to(
                    dist_util.dev())
                model_kwargs["stroke"] = model_kwargs["stroke"].repeat(3, 1)
                model_kwargs["sty"] = model_kwargs["sty"].repeat(3, 1)
            else:
                model_kwargs["mask_y"] = th.cat([th.zeros([cfg.batch_size], dtype=th.bool), th.ones([cfg.batch_size], dtype=th.bool)]).to(dist_util.dev())
                model_kwargs["y"] = model_kwargs["y"].repeat(2)
                model_kwargs["sty"] = model_kwargs["sty"].repeat(2, 1)
        else:'''
        model_kwargs["mask_y"] = th.zeros([cfg.batch_size], dtype=th.bool).to(dist_util.dev())
        '''if cfg.stroke_path is not None:
            model_kwargs["mask_stroke"] = th.zeros([cfg.batch_size], dtype=th.bool).to(dist_util.dev())'''

        # logger.log("5...")
        def model_fn(x_t, ts, **model_kwargs):
            '''if classifier_free:
                repeat_time = model_kwargs["y"].shape[0] // x_t.shape[0]
                x_t = x_t.repeat(repeat_time, 1, 1, 1)
                ts = ts.repeat(repeat_time)

                if cfg.stroke_path is not None:
                    model_output = model(x_t, ts, **model_kwargs)
                    model_output_y, model_output_stroke, model_output_uncond = model_output.chunk(3)
                    model_output = model_output_uncond + \
                                   cont_gudiance_scale * (model_output_y - model_output_uncond) + \
                                   sk_gudiance_scale * (model_output_stroke - model_output_uncond)

                else:

                    model_output = model(x_t, ts, **model_kwargs)
                    model_output_cond, model_output_uncond = model_output.chunk(2)
                    model_output = model_output_uncond + cont_gudiance_scale * (model_output_cond - model_output_uncond)

            else:'''
                # logger.log("6...")
            model_output = model(x_t, ts, **model_kwargs)
            return model_output

        # logger.log("7...")
        sample_fn = (
            diffusion.p_sample_loop if not cfg.use_ddim else diffusion.ddim_sample_loop
        )
        # sample = sample_fn(
        #     model_fn,
        #     (cfg.batch_size, 3, cfg.image_size, cfg.image_size),
        #     # con_img = con_img,
        #     clip_denoised=cfg.clip_denoised,
        #     model_kwargs=model_kwargs,
        #     device=dist_util.dev(),
        #     noise=noise,
        # )[:, 3:, :, :]
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

        gathered_labels = [
            th.zeros_like(classes) for _ in range(dist.get_world_size())
        ]
        dist.all_gather(gathered_labels, classes)
        all_labels.extend([labels.cpu().numpy() for labels in gathered_labels])
        logger.log(f"created {len(all_images) * cfg.batch_size} samples")

    # save images
    arr = np.concatenate(all_images, axis=0)
    arr = arr[: cfg.num_samples]
    label_arr = np.concatenate(all_labels, axis=0)
    label_arr = label_arr[: cfg.num_samples]
    #char2idx.keys()[char2idx.values().index(label)]
    if dist.get_rank() == 0:
        for idx, (img_sample, img_cls) in enumerate(zip(arr, label_arr)):
            img = Image.fromarray(img_sample).convert("RGB")
            img_name = gen_txt[idx] + ".png"
            #img_name = "%05d.png" % (idx)  #change the name
            img.save(os.path.join(img_save_path, img_name))
            os.chmod(os.path.join(img_save_path, img_name), 0o777)

            # remove background
            #image = Image.open(os.path.join(img_save_path, img_name))

            '''if img.mode != 'RGBA':
                img = img.convert('RGBA')

            threshold = 200  # Adjust this value according to your image

            width, height = img.size
            pixels = img.load()

            for x in range(width):
                for y in range(height):
                    r, g, b, a = pixels[x, y]

                    if r > threshold or g > threshold or b > threshold:
                        pixels[x, y] = (r, g, b, 0)  # Set the pixel to transparent
                        a = 0
                        
                    #if a != 0:
                        #pixels[x, y] = (0, 0, 0, a)

            #output_path = 'output.png'
            img.save(os.path.join(img_save_path, img_name))
            os.chmod(os.path.join(img_save_path, img_name), 0o777)'''

            dist.barrier()
        logger.log("sampling complete")


def create_cfg(cfg):
    defaults = dict(
        clip_denoised=True,
        num_samples=100,
        batch_size=16,
        use_ddim=False,
        model_path="",
        cont_scale=1.0,
        sk_scale=1.0,
        sty_img_path="",
        #gen_text_stroke_path="", # add
        #stroke_path=None,
        attention_resolutions='40, 20, 10',
    )
    defaults.update(model_and_diffusion_defaults())
    defaults.update(cfg)
    return defaults


if __name__ == "__main__":
    main()
