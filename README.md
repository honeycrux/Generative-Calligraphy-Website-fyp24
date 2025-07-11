# Generative Calligraphy Website

## Installation

### Environment Setup

Install Miniconda (See [Miniconda documentation](https://docs.conda.io/en/latest/miniconda.html)).

**For Windows, replace `openmpi` with `msmpi` in environment.yml before creating the conda environment.**

Create a conda environment and activate it. Conda will try its best to make sure the versions of packages are compatible with each other and Python 3.9 with PyTorch 1.13.1+cu116.
```bash
conda env create --name fyp23 --file=environment.yml -y
conda activate fyp23
```

### Prepare Model

Link for Downloading Trained Model: https://mycuhk-my.sharepoint.com/:f:/g/personal/1155158772_link_cuhk_edu_hk/Eo3zqXgkVwFLjVAvPxmleqYBsGZZm2jbnXmKljZ70jWwDw?e=0VNlSj

Using the link above, download trained_models_finetune > New Model > `ema_0.9999_446000.pt`. Then, in the `back-end/` directory, make the `ckpt` directory, and put `ema_0.9999_446000.pt` in ckpt.

### Run Server

(Coming soon)

## Links

Original model: https://github.com/Hxyz-123/Font-diff

Our model: https://github.com/lylee0/New-Font-Generation-from-Classic-Calligraphy

Demo Video: https://www.youtube.com/watch?v=jJgcGwrZJ-k
