"""Соединение с SQLite."""

import sqlite3
from contextlib import contextmanager

from app.config import DB_PATH


@contextmanager
def get_connection():
    """Открыть соединение, закоммитить при успехе, откатить при ошибке."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()



