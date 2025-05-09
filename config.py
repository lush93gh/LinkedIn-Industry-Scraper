"""Load environment & global settings."""

from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseSettings

# Load .env if present
load_dotenv()


class Settings(BaseSettings):
    PLAYWRIGHT_TIMEOUT: int = 30000  # ms
    USER_AGENTS_FILE: Path | None = None  # path to txt list

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
