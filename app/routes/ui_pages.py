"""HTML-страницы приложения (не API)."""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=TEMPLATES_DIR)

router = APIRouter(tags=["pages"])


@router.get("/")
async def root():
    """Редирект на страницу скачивания."""
    return RedirectResponse("/download")


@router.get("/health")
async def health():
    """Проверка, что приложение отвечает."""
    return {"ok": True}


@router.get("/download")
async def download_page(request: Request):
    """Страница запуска и прогресса скачивания."""
    return templates.TemplateResponse(request, "download.html")


@router.get("/files")
async def files_page(request: Request):
    """Страница списка файлов и расчётов."""
    return templates.TemplateResponse(request, "files.html")


