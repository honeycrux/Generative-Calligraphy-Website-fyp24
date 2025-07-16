from typing import Annotated, Optional

from fastapi import Depends

from adapter.data_access.font_generation_application import FontGenerationApplication
from adapter.data_access.in_memory_resource_storage import InMemoryResourceStorage
from application.image_access_service import ImageAccessService
from application.job_management_service import JobManagementService
from application.port_in.image_accessor_port import ImageAccessorPort
from application.port_in.job_management_port import JobManagementPort
from application.port_out.image_repository_port import ImageRepositoryPort
from application.port_out.text_generator_port import TextGeneratorPort
from domain.value.font_gen_service_config import FontGenServiceConfig

### Constants ###


OPERATE_QUEUE_INTERVAL = 2.0  # seconds
MAX_RETAIN_TIME = 60.0  # seconds


"""Terminology:

Dependency: A function or class that provides an instance of a service or resource.

Singleton: Objects that are created once and reused throughout the application.

Singleton Dependencies: Dependencies that return the singleton instances.
They are dependencies that can be replaced with mocks or stubs in tests.

Non-Singleton Dependencies: These are dependencies that create new instances each time they are called.
"""


class TextGeneratorPortProvider:
    """Provides a singleton instance of TextGeneratorPort"""

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


# Singleton dependency that returns TextGeneratorPort
get_text_generator_port = TextGeneratorPortProvider()


class ImageRepositoryPortProvider:
    """Provides a singleton instance of ImageRepositoryPort"""

    __in_memory_resource_storage: Optional[InMemoryResourceStorage] = None

    def __call__(self) -> ImageRepositoryPort:
        if self.__in_memory_resource_storage is None:
            self.__in_memory_resource_storage = InMemoryResourceStorage()
        return self.__in_memory_resource_storage

    def reset(self):
        self.__in_memory_resource_storage = None


# Singleton dependency that returns ImageRepositoryPort
get_image_repository_port = ImageRepositoryPortProvider()


def get_font_gen_service_config() -> FontGenServiceConfig:
    """Non-singleton dependency that returns FontGenServiceConfig."""
    return FontGenServiceConfig(
        operate_queue_interval=OPERATE_QUEUE_INTERVAL,
        max_retain_time=MAX_RETAIN_TIME,
    )


class JobManagementPortProvider:
    """Provides a singleton instance of JobManagementPort"""

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


# Singleton dependency that returns JobManagementPort
get_job_management_port = JobManagementPortProvider()


class ImageAccessorPortProvider:
    """Provides a singleton instance of ImageAccessorPort"""

    __image_accessor_port: Optional[ImageAccessorPort] = None

    def __call__(
        self,
        image_repository_port: Annotated[
            ImageRepositoryPort, Depends(get_image_repository_port)
        ],
    ) -> ImageAccessorPort:
        if self.__image_accessor_port is None:
            self.__image_accessor_port = ImageAccessService(
                image_repository_port=image_repository_port
            )
        return self.__image_accessor_port

    def reset(self):
        self.__image_accessor_port = None


get_image_accessor_port = ImageAccessorPortProvider()


def reset_all_dependencies():
    """Reset all singleton instances defined in this file to their initial state."""
    get_text_generator_port.reset()
    get_image_repository_port.reset()
    get_job_management_port.reset()
    get_image_accessor_port.reset()
