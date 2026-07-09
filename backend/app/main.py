"""FastAPI application entrypoint."""

from fastapi import FastAPI

from app.api.routes.assets import router as assets_router
from app.api.routes.generation import router as generation_router
from app.api.routes.generation_results import router as generation_results_router
from app.api.routes.shots import router as shots_router
from app.api.routes.scripts import router as scripts_router
from app.config import get_settings


settings = get_settings()
app = FastAPI(title=settings.app_name)
app.include_router(scripts_router)
app.include_router(shots_router)
app.include_router(assets_router)
app.include_router(generation_router)
app.include_router(generation_results_router)


@app.get("/health")
def health_check() -> dict[str, str]:
    """Return a basic health response for service checks."""

    return {"status": "ok"}
