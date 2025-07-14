from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from adapter.presentation.dependencies import get_job_management_port
from application.port_in.job_management_port import JobManagementPort

interrupt_job_router = APIRouter()


class InterruptJobRequest(BaseModel):
    job_id: str


class InterruptJobResponse(BaseModel):
    pass


@interrupt_job_router.post("/interrupt_job", response_model=InterruptJobResponse)
async def interrupt_job(
    interrupt_job_request: InterruptJobRequest,
    job_management_port: Annotated[JobManagementPort, Depends(get_job_management_port)],
):
    try:
        job_id = UUID(interrupt_job_request.job_id)
    except ValueError:
        raise HTTPException(
            status_code=422,
            detail="Invalid ID format",
        )
    job_management_port.interrupt_job(job_id=job_id)
    return InterruptJobResponse()
