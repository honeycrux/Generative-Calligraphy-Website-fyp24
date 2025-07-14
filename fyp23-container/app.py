from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html

from adapter.presentation.get_image_router import get_image_router
from adapter.presentation.interrupt_job_router import interrupt_job_router
from adapter.presentation.retrieve_job_router import retrieve_job_router
from adapter.presentation.start_job_router import start_job_router

app = FastAPI()


### Routes ###


app.include_router(start_job_router)
app.include_router(interrupt_job_router)
app.include_router(retrieve_job_router)
app.include_router(get_image_router)


### Docs ###


@app.get("/docs")
def read_docs():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")
