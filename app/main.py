from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.travel import router
from app.core.logging import setup_logging
from app.core.config import (
    validate_settings,
)


setup_logging()
validate_settings()


BASE_DIR = Path(__file__).resolve().parent.parent


app = FastAPI(
    title="TripMate AI",
    version="1.0.0",
    description=(
        "Production-style multi-agent "
        "AI travel planning system"
    ),
)


app.mount(
    "/static",
    StaticFiles(
        directory=str(
            BASE_DIR /
            "frontend" /
            "static"
        )
    ),
    name="static",
)


templates = Jinja2Templates(
    directory=str(
        BASE_DIR /
        "frontend" /
        "templates"
    )
)


app.include_router(
    router
)


@app.get(
    "/",
    response_class=HTMLResponse
)
async def home(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={}
    )


@app.get("/health")
async def health():

    return {
        "status": "ok",
        "service": "TripMate AI",
        "version": "1.0.0"
    }