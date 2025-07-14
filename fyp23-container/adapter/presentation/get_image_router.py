import io
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response
from PIL import Image
from pydantic import BaseModel

from adapter.presentation.dependencies import get_image_accessor_port
from application.port_in.image_accessor_port import ImageAccessorPort

get_image_router = APIRouter()


def get_media_type(image_bytes):
    image = Image.open(io.BytesIO(image_bytes))
    return Image.MIME[image.format]


class GetImageResponse(BaseModel):
    image: bytes


@get_image_router.get("/get_image", response_model=GetImageResponse)
async def get_image(
    image_id: str,
    image_accessor_port: Annotated[ImageAccessorPort, Depends(get_image_accessor_port)],
):

    try:
        image_uuid = UUID(image_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid ID format",
        )

    image_bytes = image_accessor_port.get_image(image_id=image_uuid)

    if image_bytes is None:
        raise HTTPException(
            status_code=404,
            detail="Image not found",
        )

    media_type = get_media_type(image_bytes)

    if media_type is None:
        raise HTTPException(
            status_code=500,
            detail="Could not determine image media type",
        )

    return Response(content=image_bytes, media_type=media_type)
