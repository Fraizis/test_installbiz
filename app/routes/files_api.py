"""HTTP API списка файлов и расчётов."""

from fastapi import APIRouter, Query

from app.api_schemas import CalculateRequest, CalculateResponse, FilesListResponse
from app.config import DEFAULT_PAGE_SIZE
from app.services import file_analytics

router = APIRouter(prefix="/api/files", tags=["files"])


@router.get("", response_model=FilesListResponse)
async def files_list(
    page: int = Query(1, ge=1),
    page_size: int = Query(DEFAULT_PAGE_SIZE, ge=1, le=100),
):
    """Список файлов с пагинацией."""
    return file_analytics.list_files_page(page, page_size)


@router.post("/calculate", response_model=CalculateResponse)
async def files_calculate(body: CalculateRequest):
    """Подсчёт цифр 0–9 по выбранным или всем файлам."""
    return file_analytics.calculate_digits(body)



