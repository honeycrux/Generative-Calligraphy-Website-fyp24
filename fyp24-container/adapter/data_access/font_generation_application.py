import asyncio
import os
from asyncio import Task
from typing import Callable, Optional, Union

import torch
from PIL import Image

from application.port_out.text_generator_port import TextGeneratorPort
from domain.value.generated_word import GeneratedWord
from domain.value.job_info import RunningJob
from domain.value.job_input import JobInput
from domain.value.running_state import RunningState
from fyp24_model.sample import arg_parse, load_fontdiffuser_pipeline, sampling
from fyp24_model.src.dpm_solver.pipeline_dpm_solver import FontDiffuserDPMPipeline


def get_file_path(filename: str):
    """Get the absolute path of the file located in the root directory of the font model project.

    Context: This file is located in the `adapter/data_access/` directory, which is 2 levels above the root.
    And we need to access the `fyp24_model/` directory.
    """
    current_script_directory = os.path.dirname(__file__)
    root_directory = os.path.dirname(os.path.dirname(current_script_directory))
    fyp24_model_directory = os.path.join(root_directory, "fyp24_model")
    return os.path.join(fyp24_model_directory, filename)


def initialize_args():
    args = arg_parse(
        args_to_parse=[
            "--ckpt_dir",
            get_file_path("ckpt"),
            "--style_image_path",
            get_file_path("lan.png"),
            "--device",
            "cuda:0" if torch.cuda.is_available() else "cpu",
            "--algorithm_type",
            "dpmsolver++",
            "--guidance_type",
            "classifier-free",
            "--guidance_scale",
            "7.5",
            "--num_inference_step",
            "20",
            "--method",
            "multistep",
            "--ttf_path",
            get_file_path("ttf/SourceHanSerifTC-VF.ttf"),
        ]
    )

    return args


def run_fontdiffuser(
    args,
    pipe,
    character: str,
    save_path: Optional[str],
    seed: Optional[int],
):
    assert len(character) == 1, "Length of character must be 1"

    args.character_input = True
    args.content_character = character

    args.seed = seed

    if save_path:
        args.save_image = True
        args.save_image_dir = save_path
    else:
        args.save_image = False
        args.save_image_dir = None

    out_image = sampling(
        args=args,
        pipe=pipe,
        content_image=None,
        style_image=None,
    )

    return out_image


class FontGenerationApplication(TextGeneratorPort):
    __seed: Optional[int]
    __image_save_path: Optional[str] = None
    __fontdiffuser_pipeline: Optional[FontDiffuserDPMPipeline] = None

    def __init__(self, seed: Optional[int], image_save_path: Optional[str]):
        self.__seed = seed
        self.__image_save_path = image_save_path

    async def __generation(
        self,
        job_input: JobInput,
        job_info: RunningJob,
        on_new_state: Callable[[RunningState], None],
        on_new_word_result: Callable[[GeneratedWord], None],
    ) -> Union[bool, str]:
        def on_new_result(
            word: str, image: Optional[Image.Image], current: int, total: int
        ):
            on_new_state(RunningState.generating(current=current, total=total))
            on_new_word_result(
                GeneratedWord.from_image(
                    word=word,
                    image=(image if image is not None else None),
                )
            )

        if job_input.input_text == "":
            return True

        args = initialize_args()

        if self.__fontdiffuser_pipeline is None:
            self.__fontdiffuser_pipeline = load_fontdiffuser_pipeline(args)

        for idx, character in enumerate(job_input.input_text):
            if character.isspace():
                out_image = None
            else:
                out_image = run_fontdiffuser(
                    args=args,
                    pipe=self.__fontdiffuser_pipeline,
                    character=character,
                    save_path=self.__image_save_path,
                    seed=self.__seed,
                )

            on_new_result(
                word=character,
                image=out_image,
                current=idx + 1,
                total=len(job_input.input_text),
            )

        return True

    def generate_text(
        self,
        job_input: JobInput,
        job_info: RunningJob,
        on_new_state: Callable[[RunningState], None],
        on_new_word_result: Callable[[GeneratedWord], None],
    ) -> Task[Union[bool, str]]:
        return asyncio.create_task(
            self.__generation(
                job_input=job_input,
                job_info=job_info,
                on_new_state=on_new_state,
                on_new_word_result=on_new_word_result,
            )
        )
