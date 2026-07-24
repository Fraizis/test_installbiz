"""Ручная проверка скачивания без UI.

Запуск из корня проекта (с активированным venv):

    python3 scripts/smoke_download.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.repository.download_jobs import get_job
from app.repository.schema import init_db
from app.workers.catalog_downloader import catalog_downloader


async def main() -> None:
    """Запустить воркер и печатать статус, пока task жив."""
    init_db()
    job = await catalog_downloader.start()
    print(
        "started:",
        job["status"],
        "nsk=",
        job.get("started_at_nsk"),
    )

    while catalog_downloader.is_running():
        await asyncio.sleep(1)
        j = get_job()
        print(
            j["status"],
            f"N={j['names_received']}",
            f"M={j['downloaded_count']}",
            f"batch={j['current_batch_size']}",
            j.get("error") or "",
        )

    print("done:", get_job())


if __name__ == "__main__":
    asyncio.run(main())



