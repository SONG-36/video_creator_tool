"""Generation task service tests."""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models.asset import Asset
from app.models.production_task import ProductionTask
from app.models.project import Project
from app.models.script import Script
from app.models.shot import Shot
from app.models.storyboard import Storyboard
from app.providers.video_provider import MockVideoProvider
from app.repositories.asset import AssetRepository
from app.repositories.generation_task import GenerationTaskRepository
from app.repositories.production import ProductionRepository
from app.services.generation_task import (
    GenerationTaskCreationError,
    GenerationTaskService,
    VideoProviderRegistry,
)


def build_test_session(tmp_path: Path) -> Session:
    database_path = tmp_path / "generation-task-service.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
    return session_factory()


def create_production_task(session: Session, status: str = "ready") -> ProductionTask:
    project = Project(name="Project Generation", product_name="Cleaner", video_goal="Video demo")
    script = Script(project=project, content="Create a final video.")
    storyboard = Storyboard(script=script)
    shot = Shot(
        storyboard=storyboard,
        shot_number=1,
        time_start=0,
        time_end=4,
        scene="Kitchen sink",
        purpose="Show final cleaning effect",
        action="Bottle enters and foam clears the stain",
        camera="Medium side dolly",
        production_type="ai_generate",
        review_status="approved",
    )
    production_task = ProductionTask(
        shot=shot,
        status=status,
        generation_mode="r2v",
        prompt="Use product identity and motion references.",
        negative_prompt="blur, flicker",
        camera="Controlled side move.",
        motion="Foam clears the stain in one pass.",
        lighting="Soft daylight hero light.",
    )
    asset = Asset(
        shot=shot,
        production_task=production_task,
        asset_type="reference_video",
        role="motion_reference",
        reference_tag="@Video1",
        requirement_note="Provide wipe-action motion timing.",
        file_path="storage/assets/motion.mp4",
        status="approved",
    )
    session.add(project)
    session.commit()
    return production_task


def build_service(session: Session) -> GenerationTaskService:
    return GenerationTaskService(
        generation_task_repository=GenerationTaskRepository(session),
        production_repository=ProductionRepository(session),
        asset_repository=AssetRepository(session),
        provider_registry=VideoProviderRegistry(providers={"mock": MockVideoProvider()}),
    )


def test_ready_production_task_can_create_and_complete_generation_task(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    production_task = create_production_task(session, status="ready")
    service = build_service(session)

    created_task = service.create_generation_task(production_task.task_id, "mock")
    assert created_task.status == "queued"
    assert created_task.request_payload["production_task_id"] == production_task.task_id
    assert created_task.request_payload["provider_request"]["accepted"] is True

    running_task = service.get_generation_task(created_task.task_id)
    assert running_task.status == "running"

    completed_task = service.get_generation_task(created_task.task_id)
    refreshed_production_task = ProductionRepository(session).get_by_id(production_task.task_id)

    assert completed_task.status == "completed"
    assert completed_task.result_payload is not None
    assert completed_task.result_payload["video_path"].endswith(f"{completed_task.task_id}.mp4")
    assert refreshed_production_task is not None
    assert refreshed_production_task.status == "completed"

    session.close()


def test_non_ready_production_task_cannot_create_generation_task(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    production_task = create_production_task(session, status="waiting_asset")
    service = build_service(session)

    try:
        service.create_generation_task(production_task.task_id, "mock")
        assert False, "Expected GenerationTaskCreationError"
    except GenerationTaskCreationError as exc:
        assert "status ready" in str(exc)

    saved_tasks = GenerationTaskRepository(session).list_by_production_task_id(production_task.task_id)
    assert saved_tasks == []

    session.close()
