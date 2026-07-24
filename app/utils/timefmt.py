"""Работа со временем: UTC для БД, НСК для UI."""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from app.config import NSK_TZ


def utc_now_iso() -> str:
    """Текущий момент в UTC (ISO-строка)."""
    return datetime.now(timezone.utc).isoformat()


def nsk_now_iso() -> str:
    """Текущий момент в часовом поясе Новосибирска (ISO)."""
    return datetime.now(ZoneInfo(NSK_TZ)).isoformat()


def to_nsk_display(iso_utc: str) -> str:
    """UTC ISO → строка для UI: ДД.ММ.ГГГГ ЧЧ:ММ:СС (НСК)."""
    try:
        dt = datetime.fromisoformat(iso_utc)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(ZoneInfo(NSK_TZ)).strftime("%d.%m.%Y %H:%M:%S")
    except Exception:
        return iso_utc


