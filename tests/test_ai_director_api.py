"""AI director API tests."""

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import get_ai_director_service
from app.db.base import Base
from app.main import app
from app.models.project import Project
from app.models.script import Script
from app.models.shot import Shot
from app.models.storyboard import Storyboard
from app.providers.director_provider import DirectorPlanResult
from app.repositories.asset import AssetRepository
from app.repositories.production import ProductionRepository
from app.repositories.shot import ShotRepository
from app.services.director import AIDirectorService


class FakeDirectorProvider:
    def generate_plan(self, shot: Shot) -> DirectorPlanResult:
        return DirectorPlanResult.model_validate(
            {
                "generation_mode": "r2v",
                "prompt": "Preserve @Image1 identity, use @Video1 for camera pace and cleaning motion.",
                "negative_prompt": "logo distortion, duplicate product, flicker",
                "camera": "Controlled lateral move ending on label close-up.",
                "motion": "Cleaning wipe crosses left to right and ends on a clean countertop.",
                "lighting": "Soft commercial daylight with highlight on the bottle cap.",
                "asset_requirement": [
                    {
                        "asset_type": "product_image",
                        "role": "identity_reference",
                        "reference_tag": "@Image1",
                        "requirement_note": "Provide hero bottle reference for identity consistency.",
                    },
                    {
                        "asset_type": "reference_video",
                        "role": "motion_reference",
                        "reference_tag": "@Video1",
                        "requirement_note": "Provide wipe-action timing and camera rhythm.",
                    },
                ],
            }
        )


def build_test_session(tmp_path: Path) -> Session:
    database_path = tmp_path / "ai-director-api.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
    return session_factory()


def create_shot(session: Session, production_type: str) -> Shot:
    project = Project(name="Project Director API", product_name="Soap", video_goal="Ad")
    script = Script(project=project, content="Generate a polished AI production plan.")
    storyboard = Storyboard(script=script)
    shot = Shot(
        storyboard=storyboard,
        shot_number=1,
        time_start=0,
        time_end=4,
        scene="Clean sink edge",
        purpose="Show the cleaning result",
        action="Bottle moves into frame and wipe cleans the surface",
        camera="Side dolly",
        review_status="approved",
        production_type=production_type,
    )
    session.add(project)
    session.commit()
    return shot


def build_ai_director_service(session: Session) -> AIDirectorService:
    return AIDirectorService(
        shot_repository=ShotRepository(session),
        production_repository=ProductionRepository(session),
        asset_repository=AssetRepository(session),
        provider=FakeDirectorProvider(),
    )


def test_generate_production_plan_api_creates_task_and_get_returns_latest_plan(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    shot = create_shot(session, production_type="ai_generate")

    app.dependency_overrides[get_ai_director_service] = lambda: build_ai_director_service(session)
    client = TestClient(app)

    generate_response = client.post(f"/shots/{shot.shot_id}/generate-production-plan")
    assert generate_response.status_code == 200

    body = generate_response.json()
    task_data = body["data"]["production_task"]

    assert task_data["shot_id"] == shot.shot_id
    assert task_data["generation_mode"] == "r2v"
    assert task_data["prompt"].startswith("Preserve @Image1")
    assert len(task_data["asset_requirement"]) == 2
    assert task_data["asset_requirement"][0]["role"] == "identity_reference"
    assert task_data["asset_requirement"][1]["reference_tag"] == "@Video1"

    saved_tasks = ProductionRepository(session).list_by_shot_id(shot.shot_id)
    saved_assets = AssetRepository(session).list_by_production_task_id(task_data["task_id"])

    assert len(saved_tasks) == 1
    assert len(saved_assets) == 2

    get_response = client.get(f"/shots/{shot.shot_id}/production-plan")
    assert get_response.status_code == 200
    assert get_response.json()["data"]["production_task"]["task_id"] == task_data["task_id"]

    app.dependency_overrides.clear()
    session.close()


def test_generate_production_plan_api_rejects_real_shoot_shot(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    shot = create_shot(session, production_type="real_shoot")

    app.dependency_overrides[get_ai_director_service] = lambda: build_ai_director_service(session)
    client = TestClient(app)

    response = client.post(f"/shots/{shot.shot_id}/generate-production-plan")

    assert response.status_code == 400
    assert "ai_generate" in response.json()["detail"]

    app.dependency_overrides.clear()
    session.close()
