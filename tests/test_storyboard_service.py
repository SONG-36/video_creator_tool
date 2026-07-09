"""Storyboard service tests."""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
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
        assert script.content
        return StoryboardGenerationResult(
            shots=[
                GeneratedShotSchema(
                    shot_number=1,
                    time_range=TimeRangeSchema(start=0, end=3),
                    scene="Dirty sink close-up",
                    purpose="Show the cleaning problem",
                    action="Camera moves toward the stain",
                    camera="Close-up push-in",
                ),
                GeneratedShotSchema(
                    shot_number=2,
                    time_range=TimeRangeSchema(start=3, end=6),
                    scene="Cleaner spray in action",
                    purpose="Show the product solving the problem",
                    action="Spray foam removes the stain",
                    camera="Medium tracking shot",
                ),
            ]
        )


def build_test_session(tmp_path: Path) -> Session:
    database_path = tmp_path / "storyboard-service.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
    return session_factory()


def test_storyboard_service_generates_storyboard_and_multiple_shots(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    project = Project(name="Project T", product_name="Cleaner", video_goal="Demo")
    script = Script(project=project, content="Show dirt first, then show the cleaner removing it.")
    session.add(project)
    session.commit()

    service = StoryboardService(
        script_repository=ScriptRepository(session),
        storyboard_repository=StoryboardRepository(session),
        shot_repository=ShotRepository(session),
        provider=FakeStoryboardProvider(),
    )

    storyboard = service.generate_storyboard(script.script_id)

    assert storyboard.script_id == script.script_id
    assert storyboard.version == 1
    assert len(storyboard.shots) == 2
    assert storyboard.shots[0].shot_number == 1
    assert storyboard.shots[0].time_start == 0
    assert storyboard.shots[0].time_end == 3
    assert storyboard.shots[0].production_type == "pending"
    assert storyboard.shots[1].review_status == "waiting_review"

    session.close()
