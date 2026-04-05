import os
from pathlib import Path

# Load repo-root .env before any DB usage (stdlib only, no python-dotenv)
_env_file = Path(__file__).resolve().parents[2] / ".env"
if _env_file.exists():
    with _env_file.open() as _f:
        for _line in _f:
            _line = _line.strip()
            if not _line or _line.startswith("#") or "=" not in _line:
                continue
            _key, _, _val = _line.partition("=")
            os.environ.setdefault(_key.strip(), _val.strip())

from fastapi import FastAPI
from app.api.prompts import router as prompts_router

app = FastAPI()
app.include_router(prompts_router)
