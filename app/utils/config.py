from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
POLICY_DIR = DATA_DIR / "policies"
VECTOR_DIR = DATA_DIR / "vector_store"
DB_PATH = BASE_DIR / "app" / "db" / "support.db"


@dataclass(frozen=True)
class Settings:
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    openai_model: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    embedding_model: str = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small")
    top_k: int = int(os.getenv("TOP_K", "4"))


settings = Settings()
