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
    asset_storage_dir: str = ""
    openai_api_key: str = ""
    openai_model: str = "gpt-5.5"
    openai_base_url: str = ""
    seedance_api_key: str = ""
    seedance_base_url: str = ""


@lru_cache
def get_settings() -> Settings:
    """Return cached application settings."""

    repo_root = Path(__file__).resolve().parents[2]
    default_database_path = repo_root / "storage" / "video_creator_tool.db"
    default_asset_storage_path = repo_root / "storage" / "assets"

    return Settings(
        app_name=os.getenv("APP_NAME", "Video Creator Tool API"),
        app_env=os.getenv("APP_ENV", "development"),
        app_host=os.getenv("APP_HOST", "127.0.0.1"),
        app_port=int(os.getenv("APP_PORT", "8000")),
        database_url=os.getenv(
            "DATABASE_URL",
            f"sqlite:///{default_database_path}",
        ),
        asset_storage_dir=os.getenv("ASSET_STORAGE_DIR", str(default_asset_storage_path)),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-5.5"),
        openai_base_url=os.getenv("OPENAI_BASE_URL", ""),
        seedance_api_key=os.getenv("SEEDANCE_API_KEY", ""),
        seedance_base_url=os.getenv("SEEDANCE_BASE_URL", ""),
    )
