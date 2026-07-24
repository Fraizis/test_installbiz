"""Создание каталогов data/ и таблиц SQLite."""

from app.config import DB_PATH, FILES_DIR
from app.repository.connection import get_connection

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS files (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    downloaded_at TEXT NOT NULL,
    path TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS download_jobs (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    status TEXT NOT NULL DEFAULT 'idle',
    started_at_nsk TEXT,
    names_received INTEGER NOT NULL DEFAULT 0,
    downloaded_count INTEGER NOT NULL DEFAULT 0,
    current_batch_size INTEGER NOT NULL DEFAULT 0,
    error TEXT,
    updated_at TEXT NOT NULL
);

INSERT OR IGNORE INTO download_jobs (id, status, updated_at)
VALUES (1, 'idle', datetime('now'));
"""


def init_db() -> None:
    """Создать data/, data/files/ и таблицы при первом запуске."""
    FILES_DIR.mkdir(parents=True, exist_ok=True)
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_connection() as conn:
        conn.executescript(SCHEMA_SQL)



