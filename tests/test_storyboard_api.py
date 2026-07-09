"""Storyboard API tests."""

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import get_storyboard_service
from app.db.base import Base
from app.main import app
from app.models.project import Project
from app.models.script import Script
from app.providers.storyboard_generator import (
    GeneratedShotSchema,
    StoryboardGenerationResult,
    TimeRangeSchema,
)
from app.repositories.script import ScriptRepository
from app.repositories.shot import ShotRepository
from app.repositories.storyboard import StoryboardRepository
from app.services.storyboard import StoryboardService


class FakeStoryboardProvider:
    def generate_storyboard(self, script: Script) -> StoryboardGenerationResult:
        return StoryboardGenerationResult(
            shots=[
                GeneratedShotSchema(
                    shot_number=1,
                    time_range=TimeRangeSchema(start=0, end=2),
                    scene="Product on a dirty table",
                    purpose="Introduce the mess",
                    action="Static shot of the stain",
                    camera="Wide static shot",
                ),
                GeneratedShotSchema(
                    shot_number=2,
                    time_range=TimeRangeSchema(start=2, end=5),
                    scene="Product wiping the surface",
                    purpose="Demonstrate cleaning effect",
                    action="Hand wipes away the stain",
                    camera="Medium side shot",
                ),
            ]
        )


def build_test_session(tmp_path: Path) -> Session:
    database_path = tmp_path / "storyboard-api.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
    return session_factory()


def build_storyboard_service(session: Session) -> StoryboardService:
    return StoryboardService(
        script_repository=ScriptRepository(session),
        storyboard_repository=StoryboardRepository(session),
        shot_repository=ShotRepository(session),
        provider=FakeStoryboardProvider(),
    )


def test_analyze_script_api_generates_storyboard_and_shots(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    project = Project(name="Project Analyze", product_name="Wipes", video_goal="TikTok ad")
    script = Script(project=project, content="Start with dirt, then show the wipe cleaning the table.")
    session.add(project)
    session.commit()

    app.dependency_overrides[get_storyboard_service] = lambda: build_storyboard_service(session)
    client = TestClient(app)

    response = client.post(f"/scripts/{script.script_id}/analyze")

    assert response.status_code == 200
    body = response.json()
    storyboard_data = body["data"]["storyboard"]

    assert storyboard_data["shot_count"] == 2
    assert storyboard_data["storyboard_id"]

    saved_storyboard = StoryboardRepository(session).get_by_id(storyboard_data["storyboard_id"])
    saved_shots = ShotRepository(session).list_by_storyboard_id(storyboard_data["storyboard_id"])

    assert saved_storyboard is not None
    assert saved_storyboard.script_id == script.script_id
    assert len(saved_shots) == 2
    assert saved_shots[0].scene == "Product on a dirty table"
    assert saved_shots[1].camera == "Medium side shot"

    app.dependency_overrides.clear()
    session.close()
