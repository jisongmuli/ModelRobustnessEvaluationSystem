"""Local configuration; private settings and runtime data are never committed."""
import os
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BACKEND_DIR / '.env', override=False)
STORAGE_DIR = Path(os.environ.get('ROBUSTNESS_STORAGE_DIR', BACKEND_DIR / 'runtime')).resolve()
STORAGE_DIR.mkdir(parents=True, exist_ok=True)
UPLOAD_DIR = STORAGE_DIR / 'uploads'
DATA_DIR = STORAGE_DIR / 'data'
RESULTS_DIR = STORAGE_DIR / 'results'
AVATAR_DIR = UPLOAD_DIR / 'avatars'
for directory in (UPLOAD_DIR, DATA_DIR, RESULTS_DIR, AVATAR_DIR):
    directory.mkdir(parents=True, exist_ok=True)
DATABASE_URL = os.environ.get('DATABASE_URL', f'sqlite:///{(STORAGE_DIR / "platform.sqlite3").as_posix()}')
CORS_ORIGINS = os.environ.get('CORS_ORIGINS', 'http://localhost:80,http://127.0.0.1:80,http://localhost:8080,http://127.0.0.1:8080').split(',')
