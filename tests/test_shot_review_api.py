"""Shot review API tests."""

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import get_shot_review_service
from app.main import app
from app.db.base import Base
from app.models.project import Project
from app.models.script import Script
from app.models.shot import Shot
from app.models.storyboard import Storyboard
from app.repositories.shot import ShotRepository
from app.repositories.shot_review import ShotReviewRepository
from app.services.review import ShotReviewService


def build_test_session(tmp_path: Path) -> Session:
    database_path = tmp_path / "shot-review-api.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
    return session_factory()


def create_shot(session: Session) -> Shot:
    project = Project(name="Project Review API", product_name="Soap", video_goal="Ad")
    script = Script(project=project, content="Review this script")
    storyboard = Storyboard(script=script)
    shot = Shot(
        storyboard=storyboard,
        shot_number=1,
        time_start=0,
        time_end=3,
        scene="Messy kitchen",
        purpose="Introduce problem",
        action="Wide shot",
        camera="Wide",
    )
    session.add(project)
    session.commit()
    return shot


def test_review_shot_api_approved_and_record_saved(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    shot = create_shot(session)

    app.dependency_overrides[get_shot_review_service] = lambda: ShotReviewService(
        shot_repository=ShotRepository(session),
        shot_review_repository=ShotReviewRepository(session),
    )
    client = TestClient(app)

    response = client.post(
        f"/shots/{shot.shot_id}/review",
        json={
            "result": "approved",
            "comment": "Storyboard is clear",
            "reviewer": "editor_1",
        },
    )

    assert response.status_code == 200
    body = response.json()
    review_data = body["data"]["review"]

    assert review_data["shot_id"] == shot.shot_id
    assert review_data["result"] == "approved"
    assert review_data["comment"] == "Storyboard is clear"
    assert review_data["reviewer"] == "editor_1"

    saved_shot = ShotRepository(session).get_by_id(shot.shot_id)
    saved_reviews = ShotReviewRepository(session).list_by_shot_id(shot.shot_id)

    assert saved_shot is not None
    assert saved_shot.review_status == "approved"
    assert len(saved_reviews) == 1
    assert saved_reviews[0].created_at is not None

    invalid_response = client.post(
        f"/shots/{shot.shot_id}/review",
        json={"result": "rejected", "comment": "second review"},
    )

    assert invalid_response.status_code == 400

    app.dependency_overrides.clear()
    session.close()
