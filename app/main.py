"""Точка входа FastAPI: lifespan, статика, подключение роутов."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.repository.schema import init_db
from app.routes import download_api, files_api, ui_pages

STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(_app: FastAPI):
    """Инициализировать схему БД и каталоги при старте."""
    init_db()
    yield


app = FastAPI(title="File Download Analyzer", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.include_router(ui_pages.router)
app.include_router(download_api.router)
app.include_router(files_api.router)



