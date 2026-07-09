"""Application configuration for the backend service."""

from dataclasses import dataclass
from functools import lru_cache
import os
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    """Runtime settings loaded from environment variables."""

    app_name: str = "Video Creator Tool API"
    app_env: str = "development"
    app_host: str = "127.0.0.1"
    app_port: int = 8000
    database_url: str = ""


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    repo_root = Path(__file__).resolve().parents[2]
    default_database_path = repo_root / "storage" / "video_creator_tool.db"

    return Settings(
        app_name=os.getenv("APP_NAME", "Video Creator Tool API"),
        app_env=os.getenv("APP_ENV", "development"),
        app_host=os.getenv("APP_HOST", "127.0.0.1"),
        app_port=int(os.getenv("APP_PORT", "8000")),
        database_url=os.getenv(
            "DATABASE_URL",
            f"sqlite:///{default_database_path}",
        ),
    )
