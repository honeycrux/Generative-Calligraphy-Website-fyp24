from typing import Annotated, Optional, Union
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from adapter.presentation.dependencies import get_job_management_port
from application.port_in.job_management_port import JobManagementPort
from domain.value.job_info import (
    CancelledJob,
    CompletedJob,
    FailedJob,
    RunningJob,
    WaitingJob,
)

retrieve_job_router = APIRouter()


class RetrieveJobResponse_JobInput(BaseModel):
    input_text: str


class RetrieveJobResponse_WaitingJob(BaseModel):
    time_start_to_queue: str
    place_in_queue: int


class RetrieveJobResponse_RunningState(BaseModel):
    name: str
    message: str


class RetrieveJobResponse_RunningJob(BaseModel):
    time_start_to_queue: str
    time_start_to_run: str
    running_state: RetrieveJobResponse_RunningState


class RetrieveJobResponse_CompletedJob(BaseModel):
    time_start_to_queue: str
    time_start_to_run: str
    time_end: str


class RetrieveJobResponse_FailedJob(BaseModel):
    time_start_to_queue: str
    time_start_to_run: str
    time_end: str
    error_message: str


class RetrieveJobResponse_CancelledJob(BaseModel):
    time_start_to_queue: str
    time_start_to_run: Optional[str]
    time_end: str


class RetrieveJobResponse_GeneratedWordLocation(BaseModel):
    word: str
    success: bool
    image_id: Optional[str]


class RetrieveJobResponse_JobResult(BaseModel):
    generated_word_locations: list[RetrieveJobResponse_GeneratedWordLocation]


class RetrieveJobResponse(BaseModel):
    job_id: str
    job_input: RetrieveJobResponse_JobInput
    job_status: str
    job_info: Union[
        RetrieveJobResponse_WaitingJob,
        RetrieveJobResponse_RunningJob,
        RetrieveJobResponse_CompletedJob,
        RetrieveJobResponse_FailedJob,
        RetrieveJobResponse_CancelledJob,
    ]
    job_result: RetrieveJobResponse_JobResult


@retrieve_job_router.get("/retrieve_job", response_model=RetrieveJobResponse)
async def retrieve_job(
    job_id: str,
    job_management_port: Annotated[JobManagementPort, Depends(get_job_management_port)],
):
    try:
        job_id_uuid = UUID(job_id)
    except ValueError:
        raise HTTPException(status_code=422, detail="Invalid ID format")

    job = job_management_port.retrieve_job(job_id=job_id_uuid)
    if job is None:
        raise HTTPException(status_code=404, detail="Job not found")

    job_input_response = RetrieveJobResponse_JobInput(
        input_text=job.job_input.input_text
    )

    job_info_response: Union[
        RetrieveJobResponse_WaitingJob,
        RetrieveJobResponse_RunningJob,
        RetrieveJobResponse_CompletedJob,
        RetrieveJobResponse_FailedJob,
        RetrieveJobResponse_CancelledJob,
    ]

    if isinstance(job.job_info, WaitingJob):
        job_info_response = RetrieveJobResponse_WaitingJob(
            time_start_to_queue=job.job_info.time_start_to_queue.isoformat(),
            place_in_queue=job.job_info.place_in_queue,
        )

    elif isinstance(job.job_info, RunningJob):
        job_info_response = RetrieveJobResponse_RunningJob(
            time_start_to_queue=job.job_info.time_start_to_queue.isoformat(),
            time_start_to_run=job.job_info.time_start_to_run.isoformat(),
            running_state=RetrieveJobResponse_RunningState(
                name=job.job_info.running_state.name,
                message=job.job_info.running_state.message,
            ),
        )

    elif isinstance(job.job_info, CompletedJob):
        job_info_response = RetrieveJobResponse_CompletedJob(
            time_start_to_queue=job.job_info.time_start_to_queue.isoformat(),
            time_start_to_run=job.job_info.time_start_to_run.isoformat(),
            time_end=job.job_info.time_end.isoformat(),
        )

    elif isinstance(job.job_info, FailedJob):
        job_info_response = RetrieveJobResponse_FailedJob(
            time_start_to_queue=job.job_info.time_start_to_queue.isoformat(),
            time_start_to_run=job.job_info.time_start_to_run.isoformat(),
            time_end=job.job_info.time_end.isoformat(),
            error_message=job.job_info.error_message,
        )

    elif isinstance(job.job_info, CancelledJob):
        job_info_response = RetrieveJobResponse_CancelledJob(
            time_start_to_queue=job.job_info.time_start_to_queue.isoformat(),
            time_start_to_run=(
                job.job_info.time_start_to_run.isoformat()
                if job.job_info.time_start_to_run
                else None
            ),
            time_end=job.job_info.time_end.isoformat(),
        )

    else:
        raise HTTPException(status_code=500, detail="Unknown job info type")

    job_result_response = RetrieveJobResponse_JobResult(
        generated_word_locations=[
            RetrieveJobResponse_GeneratedWordLocation(
                word=location.word,
                success=location.success,
                image_id=str(location.image_id) if location.image_id else None,
            )
            for location in job.job_result.generated_word_locations
        ]
    )

    return RetrieveJobResponse(
        job_id=str(job.job_id),
        job_input=job_input_response,
        job_status=job.job_status.value,
        job_info=job_info_response,
        job_result=job_result_response,
    )
