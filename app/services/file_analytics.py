"""Список файлов с НСК и подсчёт цифр."""

from pathlib import Path

from fastapi import HTTPException

from app.api_schemas import (
    CalculateRequest,
    CalculateResponse,
    FileDigitStats,
    FileItem,
    FilesListResponse,
)
from app.digit_stats import count_digits_in_file, merge_counts
from app.repository.file_records import get_all_files, get_files_by_ids, list_files
from app.utils.timefmt import to_nsk_display


def list_files_page(page: int, page_size: int) -> FilesListResponse:
    """Страница списка + downloaded_at_nsk для UI."""
    rows, total = list_files(page, page_size)
    items = [
        FileItem(
            id=r["id"],
            name=r["name"],
            downloaded_at=r["downloaded_at"],
            downloaded_at_nsk=to_nsk_display(r["downloaded_at"]),
        )
        for r in rows
    ]
    return FilesListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


def calculate_digits(body: CalculateRequest) -> CalculateResponse:
    """Подсчёт цифр по ids или по всем файлам на диске."""
    if body.mode == "all":
        rows = get_all_files()
    else:
        if not body.ids:
            raise HTTPException(status_code=400, detail="Не выбраны файлы")
        rows = get_files_by_ids(body.ids)

    if not rows:
        raise HTTPException(status_code=404, detail="Файлы не найдены")

    total = {str(d): 0 for d in range(10)}
    per_file: list[FileDigitStats] = []

    for row in rows:
        path = Path(row["path"])
        if not path.is_file():
            continue
        counts = count_digits_in_file(path)
        merge_counts(total, counts)
        per_file.append(
            FileDigitStats(id=row["id"], name=row["name"], counts=counts)
        )

    if not per_file:
        raise HTTPException(status_code=404, detail="Нет доступных файлов на диске")

    return CalculateResponse(total=total, files=per_file)



