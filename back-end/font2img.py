from PIL import Image,ImageDraw,ImageFont
import matplotlib.pyplot as plt
import os
import numpy as np
import pathlib
import argparse
from fontTools.ttLib import TTFont
import shutil


parser = argparse.ArgumentParser(description='Obtaining characters from .ttf')
parser.add_argument('--ttf_path', type=str, default='./ttf_folder',help='ttf directory')
parser.add_argument('--chara', type=str, default='./char-input.txt',help='characters')
parser.add_argument('--save_path', type=str, default='./content_folder',help='images directory')
parser.add_argument('--img_size', type=int, default=80, help='The size of generated images')
parser.add_argument('--chara_size', type=int, default=60, help='The size of generated characters')
args = parser.parse_args()

# if os.path.exists(args.save_path):
#     shutil.rmtree(args.save_path)

if not os.path.exists(args.save_path):
    os.mkdir(args.save_path)
os.chmod(args.save_path, 0o777)

with open(args.chara, 'r', encoding='utf-8') as f:
    characters = f.read().strip()

print("Font2img received input:", characters)

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

data_dir = args.ttf_path
data_root = pathlib.Path(data_dir)
print(data_root)

font_file_paths = list(data_root.glob('*.*'))  # *.ttf TTF
font_file_paths = [str(path) for path in font_file_paths]
font_file_count = len(font_file_paths)
print(font_file_count)
if font_file_count == 0:
    raise ValueError(f'No .ttf file found in the directory {data_dir}.')

seq = list()

if not os.path.exists(args.save_path):
    os.mkdir(args.save_path)

def get_char_list_from_ttf(font_file):
    f_obj = TTFont(font_file)
    m_dict = f_obj.getBestCmap()

    unicode_list = []
    for key, uni in m_dict.items():
        unicode_list.append(key)

    char_list = [chr(ch_unicode) for ch_unicode in unicode_list]
    return char_list

for idx, font_path in enumerate(font_file_paths):
    print("{}/{} ".format(idx + 1, font_file_count), font_path)
    src_font = ImageFont.truetype(font_path, size=args.chara_size)
    font_name = font_path.split('/')[-1].split('.')[0]
    # chars = get_char_list_from_ttf(item)
    img_cnt = 0
    filter_cnt = 0
    for cnt, chara in enumerate(characters):
        img = draw_example(chara, src_font, args.img_size, (args.img_size-args.chara_size)/2, (args.img_size-args.chara_size)/2)
        not_successful = args.img_size * args.img_size * 3 - np.sum(np.array(img) / 255.) < 100
        path_full = args.save_path
        # path_full = os.path.join(args.save_path, 'id_%d'%(idx))
        # if not os.path.exists(path_full):
        #     os.mkdir(path_full)
        if not_successful:
            filter_cnt += 1
        else:
            img_cnt += 1
            img.save(os.path.join(path_full, chara + '.png'))
            os.chmod(os.path.join(path_full, chara + '.png'), 0o777)
            # img.save(os.path.join(path_full, "%05d.png" % (cnt)))
    print(img_cnt, 'characters are generated as images')
    print(filter_cnt, 'characters are missing in this font')
