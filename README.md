# Generative Calligraphy Website

## Installation

### Environment Setup

Install Miniconda (See [Miniconda documentation](https://docs.conda.io/en/latest/miniconda.html)).

**If a Windows machine is used, in `fyp23-container/environment.yml`, replace `openmpi` with `msmpi` before continuing the installation.**

Install all conda environments with the following command (it takes a while to complete):
```sh
sh scripts/setup-conda-envs.sh
```

### Install Traefik

Go to [Traefik releases](https://github.com/traefik/traefik/releases). Download the Traefik binary appropriate for your machine. Rename the binary as `traefik` and place it in the project root.

## Prepare Models

#### Prepare FYP23 Model

Link for Downloading Trained Model: https://mycuhk-my.sharepoint.com/:f:/g/personal/1155158772_link_cuhk_edu_hk/Eo3zqXgkVwFLjVAvPxmleqYBsGZZm2jbnXmKljZ70jWwDw?e=0VNlSj

Using the link above, download trained_models_finetune > New Model > `ema_0.9999_446000.pt`. Then, in the `fyp23-container/fyp23_model/` directory, create the `ckpt` directory, and put `ema_0.9999_446000.pt` into the ckpt directory.

#### Prepare FYP24 Model

(Coming soon)

## Run Server

Running the server requires running each container in separate shells.

#### Serve Frontend

Open a new shell and run:
```sh
sh scripts/serve-frontend.sh
```

The website can be accessed on `<ip-address>:6700`.

#### Run Backend Proxy

Open a new shell and run:
```sh
sh scripts/run-traefik.sh
```

The proxy will run on `<ip-address>:6701`.

#### Run FYP23 Container

Open a new shell and run:
```sh
sh scripts/run-fyp23.sh
```

This container is accessed through `<ip-address>:6701/fyp23`.

#### Run FYP24 Container

Open a new shell and run:
```sh
sh scripts/run-fyp24.sh
```

This container is accessed through `<ip-address>:6701/fyp24`.

## Develop

#### Run Tests (FYP23 Container, FYP24 Container)

To run the tests on a model container, use the corresponding conda environment and go to the corresponding directory. Below, we use FYP23 Container as an example.

```sh
conda activate fyp23-container
cd fyp23-container
```

To run all tests, run:
```sh
pytest tests/
```

To skip slow tests, (i.e. tests that involves image generation), run:
```sh
pytest tests/ -m "not slow"
```

Additionally, we provide some CLI tests to test the CLI that the model originally provides. These tests does not cover all usecases of the CLI and serve only to demonstrate one way to use the CLI. The CLI tests does not correlate to the correctness of the backend application, since the CLI is not used in the backend application.

To skip CLI tests, run:
```sh
pytest tests/ -m "not cli"
```

## Links

These links are provided by the FYP23 group.
- Original model: https://github.com/Hxyz-123/Font-diff
- Our repository: https://github.com/lylee0/New-Font-Generation-from-Classic-Calligraphy
- Demo Video: https://www.youtube.com/watch?v=jJgcGwrZJ-k

These links are provided by the FYP24 group.
- Original model: https://github.com/yeungchenwa/FontDiffuser
- Our repository: https://github.com/honeycrux/FontDiffuser-Classic-Calligraphy
