from fastapi import FastAPI
import os

from app.api.v1 import tasks, auth
from app.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)

APP_TITLE = "Task Manager"
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
APP_DESCRIPTION = (
    "Task Manager service — CRUD for user tasks. Swagger UI available at /docs."
)

OPENAPI_URL = "/api/v1/openapi.json"
DOCS_URL = "/docs"
REDOC_URL = "/redoc"


app = FastAPI(
    title=APP_TITLE,
    version=APP_VERSION,
    description=APP_DESCRIPTION,
    docs_url=DOCS_URL,
    redoc_url=REDOC_URL,
    openapi_url=OPENAPI_URL,
)

app.include_router(tasks.router, prefix="/api/v1", tags=["tasks"])
app.include_router(auth.router, prefix="/api/v1", tags=["auth"])


@app.get("/health", tags=["health"])
def health():
    logger.debug("health.check")
    return {"status": "ok"}
