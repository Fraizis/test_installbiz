from pathlib import Path

from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

EXTERNAL_API_BASE = os.getenv("EXTERNAL_API_BASE", "http://91.199.149.128:18001").rstrip("/")
X_CANDIDATE_ID = os.getenv("X_CANDIDATE_ID", "candidate-local")
REQUEST_PAUSE_MS = int(os.getenv("REQUEST_PAUSE_MS", "300"))

DATA_DIR = BASE_DIR / "data"
FILES_DIR = DATA_DIR / "files"
DB_PATH = DATA_DIR / "app.db"

DEFAULT_PAGE_SIZE = 20
NSK_TZ = "Asia/Novosibirsk"

