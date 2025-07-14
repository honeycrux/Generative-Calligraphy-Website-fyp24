from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from adapter.presentation.dependencies import get_job_management_port
from application.port_in.job_management_port import JobManagementPort
from domain.value.job_input import JobInput

start_job_router = APIRouter()


class StartJobRequest(BaseModel):
    input_text: str


class StartJobResponse(BaseModel):
    job_id: str


@start_job_router.post("/start_job", response_model=StartJobResponse)
async def start_job(
    start_job_request: StartJobRequest,
    job_management_port: Annotated[JobManagementPort, Depends(get_job_management_port)],
):
    job_input = JobInput(input_text=start_job_request.input_text)
    job_id = job_management_port.start_job(job_input=job_input)
    return StartJobResponse(job_id=str(job_id))
