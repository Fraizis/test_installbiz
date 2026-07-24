"""HTTP-клиент внешнего каталога файлов: 429/403 + Retry-After."""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Awaitable, Callable

import httpx

from app.config import EXTERNAL_API_BASE, X_CANDIDATE_ID
from app.repository.download_jobs import update_job

ShouldStop = Callable[[], Awaitable[bool]]  # True = остановиться после ожидания


class CatalogApiClient:
    """Клиент внешнего API: names / download ZIP / mark downloaded."""

    def __init__(self, *, should_stop: ShouldStop | None = None) -> None:
        self._should_stop = should_stop
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> CatalogApiClient:
        self._client = httpx.AsyncClient(
            base_url=EXTERNAL_API_BASE,
            headers={"X-Candidate-Id": X_CANDIDATE_ID},
            timeout=360.0,
        )
        return self

    async def __aexit__(self, *exc) -> None:
        if self._client:
            await self._client.aclose()

    async def get_names(self) -> list[str]:
        """GET /api/files/names. Пустой список = каталог исчерпан."""
        response = await self._request("GET", "/api/files/names")
        return list(response.json().get("file_names") or [])

    async def download_zip(self, names: list[str]) -> bytes:
        """POST /api/files/download → тело ZIP."""
        response = await self._request(
            "POST",
            "/api/files/download",
            json={"file_names": names},
        )
        return response.content

    async def mark_downloaded(self, names: list[str]) -> None:
        """POST /api/files/downloaded — подтвердить приём порции."""
        await self._request(
            "POST",
            "/api/files/downloaded",
            json={"file_names": names},
        )

    async def _request(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Запрос с ожиданием Retry-After при 429/403."""
        assert self._client is not None
        while True:
            response = await self._client.request(method, url, **kwargs)
            if response.status_code not in (429, 403):
                response.raise_for_status()
                return response

            wait_s = self._parse_retry_after(response)
            detail = ""
            try:
                detail = response.json().get("detail", "")
            except Exception:
                detail = response.text[:200]

            update_job(
                status="paused_rate_limit",
                error=f"{response.status_code}: жду {wait_s:.0f}с. {detail}".strip(),
            )
            await asyncio.sleep(wait_s)

            if self._should_stop and await self._should_stop():
                update_job(status="paused", error=None)
                raise asyncio.CancelledError()

            update_job(status="running", error=None)

    @staticmethod
    def _parse_retry_after(response: httpx.Response) -> float:
        """Секунды ожидания из Retry-After (число или HTTP-date)."""
        raw = response.headers.get("Retry-After")
        if not raw:
            return 5.0
        try:
            return max(float(raw), 1.0)
        except ValueError:
            try:
                dt = parsedate_to_datetime(raw)
                if dt.tzinfo is None:
                    dt = dt.replace(tzinfo=timezone.utc)
                return max((dt - datetime.now(timezone.utc)).total_seconds(), 1.0)
            except Exception:
                return 5.0


