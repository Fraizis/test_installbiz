"""SQL-доступ к таблице files (метаданные скачанных файлов)."""

from pathlib import Path

from app.repository.connection import get_connection
from app.utils.timefmt import utc_now_iso


def upsert_file(name: str, path: Path, downloaded_at: str | None = None) -> None:
    """Вставить или обновить файл по UNIQUE(name)."""
    ts = downloaded_at or utc_now_iso()
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO files (name, downloaded_at, path)
            VALUES (?, ?, ?)
            ON CONFLICT(name) DO UPDATE SET
                downloaded_at = excluded.downloaded_at,
                path = excluded.path
            """,
            (name, ts, str(path)),
        )


def list_files(page: int, page_size: int) -> tuple[list[dict], int]:
    """Страница файлов: (rows, total), сортировка downloaded_at DESC."""
    offset = (page - 1) * page_size
    with get_connection() as conn:
        total = conn.execute("SELECT COUNT(*) AS c FROM files").fetchone()["c"]
        rows = conn.execute(
            """
            SELECT id, name, downloaded_at, path
            FROM files
            ORDER BY downloaded_at DESC
            LIMIT ? OFFSET ?
            """,
            (page_size, offset),
        ).fetchall()
        return [dict(r) for r in rows], total


def get_files_by_ids(ids: list[int]) -> list[dict]:
    """Файлы по списку id. Пустой ids → []."""
    if not ids:
        return []
    placeholders = ",".join("?" * len(ids))
    with get_connection() as conn:
        rows = conn.execute(
            f"SELECT id, name, downloaded_at, path FROM files WHERE id IN ({placeholders})",
            ids,
        ).fetchall()
        return [dict(r) for r in rows]


def get_all_files() -> list[dict]:
    """Все файлы, downloaded_at DESC."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, name, downloaded_at, path FROM files ORDER BY downloaded_at DESC"
        ).fetchall()
        return [dict(r) for r in rows]


