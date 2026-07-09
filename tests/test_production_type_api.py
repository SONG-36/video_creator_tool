"""Production type API tests."""

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import get_production_type_service
from app.db.base import Base
from app.main import app
from app.models.project import Project
from app.models.script import Script
from app.models.shot import Shot
from app.models.storyboard import Storyboard
from app.repositories.shot import ShotRepository
from app.services.production_type import ProductionTypeService


def build_test_session(tmp_path: Path) -> Session:
    database_path = tmp_path / "production-type-api.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
    return session_factory()


def create_shot(session: Session, review_status: str = "approved") -> Shot:
    project = Project(name="Project Production API", product_name="Soap", video_goal="Ad")
    script = Script(project=project, content="Pick a production type")
    storyboard = Storyboard(script=script)
    shot = Shot(
        storyboard=storyboard,
        shot_number=1,
        time_start=0,
        time_end=3,
        scene="Kitchen counter",
        purpose="Setup scene",
        action="Show messy counter",
        camera="Wide shot",
        review_status=review_status,
    )
    session.add(project)
    session.commit()
    return shot


def test_production_type_api_accepts_approved_shots_and_rejects_invalid_cases(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    approved_shot = create_shot(session, review_status="approved")
    waiting_shot = create_shot(session, review_status="waiting_review")

    app.dependency_overrides[get_production_type_service] = lambda: ProductionTypeService(
        shot_repository=ShotRepository(session),
    )
    client = TestClient(app)

    real_shoot_response = client.post(
        f"/shots/{approved_shot.shot_id}/production-type",
        json={"production_type": "real_shoot"},
    )
    assert real_shoot_response.status_code == 200
    assert real_shoot_response.json()["data"]["shot"]["production_type"] == "real_shoot"

    approved_shot_second = create_shot(session, review_status="approved")
    ai_generate_response = client.post(
        f"/shots/{approved_shot_second.shot_id}/production-type",
        json={"production_type": "ai_generate"},
    )
    assert ai_generate_response.status_code == 200
    assert ai_generate_response.json()["data"]["shot"]["production_type"] == "ai_generate"

    waiting_response = client.post(
        f"/shots/{waiting_shot.shot_id}/production-type",
        json={"production_type": "real_shoot"},
    )
    assert waiting_response.status_code == 400

    invalid_type_response = client.post(
        f"/shots/{approved_shot.shot_id}/production-type",
        json={"production_type": "bad_type"},
    )
    assert invalid_type_response.status_code == 400

    app.dependency_overrides.clear()
    session.close()
