from __future__ import annotations

import os
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

ROOT_DIR = Path(__file__).resolve().parents[2]

load_dotenv(ROOT_DIR / ".env")


class Settings(BaseModel):
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


settings = Settings()

DATA_DIR = ROOT_DIR / "data"
POLICY_DIR = DATA_DIR / "policies"
VECTOR_STORE_DIR = DATA_DIR / "vector_store"

APP_DIR = ROOT_DIR / "app"
DB_DIR = APP_DIR / "db"
DB_PATH = DB_DIR / "support.db"

ASSETS_DIR = ROOT_DIR / "assets"