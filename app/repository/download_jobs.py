"""SQL-доступ к таблице download_jobs (одна запись id=1)."""

from app.repository.connection import get_connection
from app.utils.timefmt import utc_now_iso


def get_job() -> dict:
    """Вернуть единственную запись download_jobs."""
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM download_jobs WHERE id = 1").fetchone()
        return dict(row)


def update_job(**fields) -> dict:
    """Обновить поля джоба; всегда проставляет updated_at (UTC ISO)."""
    if not fields:
        return get_job()
    fields["updated_at"] = utc_now_iso()
    cols = ", ".join(f"{k} = ?" for k in fields)
    values = list(fields.values())
    with get_connection() as conn:
        conn.execute(f"UPDATE download_jobs SET {cols} WHERE id = 1", values)
        row = conn.execute("SELECT * FROM download_jobs WHERE id = 1").fetchone()
        return dict(row)


