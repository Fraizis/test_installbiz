"""Pydantic-схемы запросов и ответов API (не таблицы БД)."""

from typing import Literal

from pydantic import BaseModel, Field


class DownloadStatusResponse(BaseModel):
    """Статус фонового джоба скачивания для UI/API."""

    status: str
    started_at_nsk: str | None = None
    names_received: int = 0
    downloaded_count: int = 0
    current_batch_size: int = 0
    error: str | None = None
    message: str | None = None


class FileItem(BaseModel):
    """Один файл в списке: метаданные + время в НСК для UI."""

    id: int
    name: str
    downloaded_at: str
    downloaded_at_nsk: str


class FilesListResponse(BaseModel):
    """Страница списка файлов с пагинацией."""

    items: list[FileItem]
    total: int
    page: int
    page_size: int


class CalculateRequest(BaseModel):
    """Запрос на подсчёт цифр: по ids или по всем файлам."""

    mode: Literal["ids", "all"] = "ids"
    ids: list[int] = Field(default_factory=list)


class FileDigitStats(BaseModel):
    """Частота цифр 0–9 в одном файле."""

    id: int
    name: str
    counts: dict[str, int]


class CalculateResponse(BaseModel):
    """Общая статистика и разбивка по файлам."""

    total: dict[str, int]
    files: list[FileDigitStats]



