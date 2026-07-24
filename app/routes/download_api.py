"""HTTP API скачивания: start / stop / status."""

from fastapi import APIRouter

from app.api_schemas import DownloadStatusResponse
from app.services import download_control

router = APIRouter(prefix="/api/download", tags=["download"])


@router.post("/start", response_model=DownloadStatusResponse)
async def download_start():
    """Запустить фоновое скачивание."""
    return await download_control.start()


@router.post("/stop", response_model=DownloadStatusResponse)
async def download_stop():
    """Поставить скачивание на паузу."""
    return await download_control.stop()


@router.get("/status", response_model=DownloadStatusResponse)
async def download_status():
    """Получить текущий статус и прогресс."""
    return download_control.current_status()



