from typing import Optional

from adapter.presentation.dependencies import reset_all_dependencies
from application.port_out.image_repository_port import ImageRepositoryPort
from application.port_out.text_generator_port import TextGeneratorPort
from domain.value.font_gen_service_config import FontGenServiceConfig
from tests.application.image_repository_stub import ImageRepositoryStub
from tests.application.text_generator_stub import TextGeneratorStub

### Constants ###


JOB_PROCESSING_TIME = 0.1  # seconds
OPERATE_QUEUE_INTERVAL = 0.01  # seconds
MAX_RETAIN_TIME = 0.3  # seconds
TINY_BUFFER = 0.04  # seconds; we found that 0.03 sometimes fails due to timing issues

### Dependency Overrides ###


class TextGeneratorProvider:
    __text_generator_port: Optional[TextGeneratorPort] = None
    __simulate_success: bool

    def __init__(self, simulate_success: bool):
        self.__simulate_success = simulate_success

    def __call__(self) -> TextGeneratorPort:
        if self.__text_generator_port is None:
            self.__text_generator_port = TextGeneratorStub(
                job_processing_time=JOB_PROCESSING_TIME,
                simulate_success=self.__simulate_success,
            )
        return self.__text_generator_port

    def reset(self):
        self.__text_generator_port = None


override_text_generator_port = TextGeneratorProvider(simulate_success=True)

override_text_generator_port_that_fails = TextGeneratorProvider(simulate_success=False)


class ImageRepositoryProvider:
    __image_repository_port: Optional[ImageRepositoryPort] = None

    def __call__(self) -> ImageRepositoryPort:
        if self.__image_repository_port is None:
            self.__image_repository_port = ImageRepositoryStub()
        return self.__image_repository_port

    def reset(self):
        self.__image_repository_port = None


override_image_repository_port = ImageRepositoryProvider()


class FontGenServiceConfigProvider:
    __font_gen_service_config: Optional[FontGenServiceConfig] = None

    def __call__(self) -> FontGenServiceConfig:
        if self.__font_gen_service_config is None:
            self.__font_gen_service_config = FontGenServiceConfig(
                operate_queue_interval=OPERATE_QUEUE_INTERVAL,
                max_retain_time=MAX_RETAIN_TIME,
            )
        return self.__font_gen_service_config

    def reset(self):
        self.__font_gen_service_config = None


override_font_gen_service_config = FontGenServiceConfigProvider()


def reset_all_test_dependencies():
    """Reset all singleton instances used in tests to their initial state."""

    override_text_generator_port.reset()
    override_text_generator_port_that_fails.reset()
    override_image_repository_port.reset()
    override_font_gen_service_config.reset()

    reset_all_dependencies()
