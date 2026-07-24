"""Оркестрация скачивания и текст статуса для UI."""

from app.api_schemas import DownloadStatusResponse
from app.repository.download_jobs import get_job
from app.workers.catalog_downloader import catalog_downloader


def status_message(job: dict) -> str:
    """Человекочитаемое сообщение по полям download_jobs."""
    status = job["status"]
    n = job["names_received"]
    m = job["downloaded_count"]
    batch = job["current_batch_size"]

    if status == "idle":
        return "Скачивание ещё не запускалось."
    if status == "paused_rate_limit":
        return f"Получено {n} названий файлов, пауза из‑за лимита. Скачано {m} из {n}."
    if status == "running":
        if batch > 0:
            return f"Получено {n} названий файлов, скачиваю… скачано {m} из {n}."
        return f"Получено {n} названий файлов, скачано {m} из {n}."
    if status == "paused":
        return (
            f"Пауза. Получено {n} названий, скачано {m} из {n}. "
            "Нажмите «Скачать данные», чтобы продолжить."
        )
    if status == "completed":
        return f"Готово. Получено {n} названий файлов, скачано {m} из {n}."
    if status == "failed":
        return job.get("error") or "Ошибка скачивания."
    return status


def job_to_response(job: dict) -> DownloadStatusResponse:
    """Собрать ответ API из строки download_jobs."""
    return DownloadStatusResponse(
        status=job["status"],
        started_at_nsk=job.get("started_at_nsk"),
        names_received=job["names_received"],
        downloaded_count=job["downloaded_count"],
        current_batch_size=job["current_batch_size"],
        error=job.get("error"),
        message=status_message(job),
    )


async def start() -> DownloadStatusResponse:
    """Запустить или продолжить фоновое скачивание."""
    return job_to_response(await catalog_downloader.start())


async def stop() -> DownloadStatusResponse:
    """Поставить скачивание на паузу после текущего чанка."""
    return job_to_response(await catalog_downloader.stop())


def current_status() -> DownloadStatusResponse:
    """Текущий статус без побочных эффектов."""
    return job_to_response(get_job())


