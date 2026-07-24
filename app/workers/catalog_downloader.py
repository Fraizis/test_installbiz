"""Фоновый воркер каталога: names → ZIP → диск → mark."""

import asyncio
import io
import zipfile
from datetime import datetime, timezone

from app.clients.catalog_api import CatalogApiClient
from app.config import FILES_DIR, REQUEST_PAUSE_MS
from app.repository.download_jobs import get_job, update_job
from app.repository.file_records import upsert_file
from app.utils.timefmt import nsk_now_iso

CHUNK_SIZE = 3


class CatalogDownloader:
    """Один asyncio.Task на процесс; start/stop через флаг паузы."""

    def __init__(self) -> None:
        self._task: asyncio.Task | None = None
        self._lock = asyncio.Lock()
        self._stop_requested = False

    def is_running(self) -> bool:
        """Есть ли незавершённый task."""
        return self._task is not None and not self._task.done()

    async def start(self) -> dict:
        """Новый прогон или продолжение после paused/failed. Вернуть job."""
        async with self._lock:
            if self.is_running():
                return get_job()

            self._stop_requested = False
            job = get_job()

            if job["status"] in ("paused", "failed"):
                # докачка: счётчики и started_at_nsk не трогаем
                job = update_job(status="running", error=None)
            else:
                job = update_job(
                    status="running",
                    started_at_nsk=nsk_now_iso(),
                    names_received=0,
                    downloaded_count=0,
                    current_batch_size=0,
                    error=None,
                )

            self._task = asyncio.create_task(self._run())
            return job

    async def stop(self) -> dict:
        """Запросить паузу; цикл остановится после текущего чанка."""
        async with self._lock:
            job = get_job()
            if not self.is_running():
                if job["status"] in ("running", "paused_rate_limit"):
                    return update_job(status="paused", error=None)
                return job

            self._stop_requested = True
            return update_job(
                status="paused",
                error="Остановка после текущего чанка…",
            )

    async def _run(self) -> None:
        """Цикл до пустого names / pause / error."""
        pause = REQUEST_PAUSE_MS / 1000.0

        async def should_stop() -> bool:
            return self._stop_requested

        try:
            async with CatalogApiClient(should_stop=should_stop) as api:
                while True:
                    if self._stop_requested:
                        update_job(status="paused", current_batch_size=0, error=None)
                        return

                    names = await api.get_names()
                    if not names:
                        update_job(status="completed", current_batch_size=0, error=None)
                        return

                    batch_size = len(names)
                    job = get_job()
                    update_job(
                        status="running",
                        names_received=job["names_received"] + batch_size,
                        current_batch_size=batch_size,
                        error=None,
                    )

                    batch_downloaded = 0
                    for i in range(0, len(names), CHUNK_SIZE):
                        if self._stop_requested:
                            # имена порции уже в N, нескачанные снова придут из API —
                            # вычитаем остаток, чтобы N не раздувался
                            remaining = batch_size - batch_downloaded
                            job = get_job()
                            update_job(
                                status="paused",
                                names_received=max(0, job["names_received"] - remaining),
                                current_batch_size=0,
                                error=None,
                            )
                            return

                        chunk = names[i : i + CHUNK_SIZE]
                        content = await api.download_zip(chunk)
                        self._save_zip(content)
                        await api.mark_downloaded(chunk)

                        batch_downloaded += len(chunk)
                        job = get_job()
                        update_job(
                            status="running",
                            downloaded_count=job["downloaded_count"] + len(chunk),
                            current_batch_size=batch_size,
                            error=None,
                        )
                        if pause > 0:
                            await asyncio.sleep(pause)

                    if pause > 0:
                        await asyncio.sleep(pause)

        except asyncio.CancelledError:
            update_job(status="paused", error=None)
        except Exception as exc:
            update_job(status="failed", error=str(exc))

    def _save_zip(self, content: bytes) -> None:
        """Распаковать ZIP в FILES_DIR и upsert метаданных (downloaded_at UTC)."""
        FILES_DIR.mkdir(parents=True, exist_ok=True)
        now = datetime.now(timezone.utc).isoformat()
        with zipfile.ZipFile(io.BytesIO(content)) as zf:
            for info in zf.infolist():
                if info.is_dir():
                    continue
                filename = info.filename.split("/")[-1]
                if not filename:
                    continue
                target = FILES_DIR / filename
                with zf.open(info) as src, open(target, "wb") as dst:
                    dst.write(src.read())
                upsert_file(filename, target, downloaded_at=now)


catalog_downloader = CatalogDownloader()


