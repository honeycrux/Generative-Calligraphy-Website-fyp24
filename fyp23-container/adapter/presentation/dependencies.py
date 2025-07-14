from typing import Annotated, Any, Optional

from fastapi import Depends

from adapter.data_access.font_generation_application import FontGenerationApplication
from adapter.data_access.in_memory_resource_storage import InMemoryResourceStorage
from application.job_management_service import JobManagementService
from application.port_in.job_management_port import JobManagementPort
from application.port_out.image_repository_port import ImageRepositoryPort
from application.port_out.text_generator_port import TextGeneratorPort
from domain.value.font_gen_service_config import FontGenServiceConfig

### Constants ###


OPERATE_QUEUE_INTERVAL = 3.0  # seconds
MAX_RETAIN_TIME = 60.0  # seconds


### Singletons and Singleton Dependencies ###
### Singletons: Objects that are created once and reused throughout the application. ###
### Singleton Dependencies: Dependencies that return the singleton instances. ###
### They are dependencies that can be replaced with mocks or stubs in tests. ###


class TextGeneratorPortProvider:
    __font_generation_application: Optional[FontGenerationApplication] = None

    def __call__(self) -> TextGeneratorPort:
        if self.__font_generation_application is None:
            self.__font_generation_application = FontGenerationApplication(
                seed=None,
                image_save_path=None,
            )
        return self.__font_generation_application

    def reset(self):
        self.__font_generation_application = None


get_text_generator_port = TextGeneratorPortProvider()


class ImageRepositoryPortProvider:
    __in_memory_resource_storage: Optional[InMemoryResourceStorage] = None

    def __call__(self) -> ImageRepositoryPort:
        if self.__in_memory_resource_storage is None:
            self.__in_memory_resource_storage = InMemoryResourceStorage()
        return self.__in_memory_resource_storage

    def reset(self):
        self.__in_memory_resource_storage = None


get_image_repository_port = ImageRepositoryPortProvider()


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


get_font_gen_service_config = FontGenServiceConfigProvider()


class JobManagementPortProvider:
    __job_management_service: Optional[JobManagementPort] = None

    def __call__(
        self,
        text_generator_port: Annotated[
            TextGeneratorPort, Depends(get_text_generator_port)
        ],
        image_repository_port: Annotated[
            ImageRepositoryPort, Depends(get_image_repository_port)
        ],
        font_gen_service_config: Annotated[
            FontGenServiceConfig, Depends(get_font_gen_service_config)
        ],
    ) -> JobManagementPort:
        if self.__job_management_service is None:
            self.__job_management_service = JobManagementService(
                text_generator_port=text_generator_port,
                image_repository_port=image_repository_port,
                font_gen_service_config=font_gen_service_config,
            )
        return self.__job_management_service

    def reset(self):
        self.__job_management_service = None


get_job_management_port = JobManagementPortProvider()


def reset_all_dependencies():
    """Reset all singleton instances defined in this file to their initial state."""
    get_text_generator_port.reset()
    get_image_repository_port.reset()
    get_font_gen_service_config.reset()
    get_job_management_port.reset()


### Non-Singleton Dependencies: These are dependencies that create new instances each time they are called. ###
