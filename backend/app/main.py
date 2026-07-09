"""FastAPI application entrypoint."""

from fastapi import FastAPI

from app.config import get_settings


settings = get_settings()
app = FastAPI(title=settings.app_name)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return a basic health response for service checks."""

    return {"status": "ok"}
