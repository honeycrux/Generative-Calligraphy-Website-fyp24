from fastapi import FastAPI
from fastapi.openapi.docs import get_swagger_ui_html

app = FastAPI()

### Routes ###


### Docs ###


@app.get("/docs")
def read_docs():
    return get_swagger_ui_html(openapi_url="/openapi.json", title="docs")
