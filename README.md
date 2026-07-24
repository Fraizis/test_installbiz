# Сервис скачивания и анализа файлов

Веб-сервис на FastAPI: скачивает каталог текстовых файлов в фоновом режиме через внешнее API (порциями, с обработкой rate limit), сохраняет их локально и считает частоту цифр 0–9 по выбранным файлам.

Внешнее API: http://91.199.149.128:18001/docs

## Стек

- Python 3.12+
- FastAPI + Uvicorn
- SQLite
- Jinja2 + vanilla JS

## Описание переменных окружения(.env)

- EXTERNAL_API_BASE - Базовый URL внешнего API 
- X_CANDIDATE_ID - Идентификатор кандидата (чтобы скачать каталог заново, смените значение)
- REQUEST_PAUSE_MS - Пауза между запросами к внешнему API

## Время

- В БД downloaded_at хранится в UTC (ISO).
- В интерфейсе и в поле downloaded_at_nsk показывается время Новосибирска (Asia/Novosibirsk).
- started_at_nsk в джобе скачивания сразу сохраняется по НСК.

## Структура

  app/
- main.py           # приложение, страницы
- config.py         # настройки
- db.py             # SQLite
- downloader.py     # клиент внешнего API
- stats.py          # подсчёт цифр
- models.py         # схемы ответов
- routers/          # API download / files
- templates/        # HTML
- static/           # CSS, JS
- data/               # app.db и скачанные файлы (создаётся автоматически)
- scripts/smoke_download.py  # проверка downloader без UI

## API сервиса

- GET / — редирект на /api/download
- POST /api/download/start — запуск скачивания
- GET /api/download/status — статус и прогресс
- GET /api/files?page=&page_size= — список файлов
- POST /api/files/calculate — { "mode": "ids"|"all", "ids": [...] } - статистика

## Быстрый старт

    python -m venv .venv
    source .venv/bin/activate    # Windows: .venv\Scripts\activate
    pip install -r requirements.txt
    cp .env.example .env
    uvicorn app.main:app --reload --port 8000

## Ручная проверка без UI

    python3 scripts/smoke_download.py


