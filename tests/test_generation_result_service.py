"""Generation result service tests."""

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
from app.repositories.generation_result import GenerationResultRepository
from app.repositories.generation_review import GenerationReviewRepository
from app.repositories.generation_task import GenerationTaskRepository
from app.repositories.production import ProductionRepository
from app.services.generation_result import GenerationResultService
from app.services.generation_review import GenerationReviewService
from app.services.generation_task import GenerationTaskService, VideoProviderRegistry


def build_test_session(tmp_path: Path) -> Session:
    database_path = tmp_path / "generation-result-service.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
    return session_factory()


def create_production_task(session: Session, status: str = "ready") -> ProductionTask:
    project = Project(name="Project Result Review", product_name="Soap", video_goal="Ad")
    script = Script(project=project, content="Create a reviewable generated clip.")
    storyboard = Storyboard(script=script)
    shot = Shot(
        storyboard=storyboard,
        shot_number=1,
        time_start=0,
        time_end=5,
        scene="Countertop cleanup",
        purpose="Review generated video",
        action="Bottle glides in and foam wipes the stain",
        camera="Side tracking shot",
        production_type="ai_generate",
        review_status="approved",
    )
    production_task = ProductionTask(
        shot=shot,
        status=status,
        generation_mode="i2v",
        prompt="Create a polished hero shot from approved references.",
        negative_prompt="distortion, blur",
        camera="Controlled side track.",
        motion="Bottle enters, wipe clears stain, end on clean frame.",
        lighting="Soft daylight with clean rim.",
    )
    asset = Asset(
        shot=shot,
        production_task=production_task,
        asset_type="product_image",
        role="identity_reference",
        reference_tag="@Image1",
        requirement_note="Provide the hero packshot.",
        file_path="storage/assets/product.png",
        status="approved",
    )
    session.add(project)
    session.commit()
    return production_task


def build_generation_task_service(session: Session) -> GenerationTaskService:
    return GenerationTaskService(
        generation_task_repository=GenerationTaskRepository(session),
        generation_result_repository=GenerationResultRepository(session),
        production_repository=ProductionRepository(session),
        asset_repository=AssetRepository(session),
        provider_registry=VideoProviderRegistry(providers={"mock": MockVideoProvider()}),
    )


def create_completed_generation_result(session: Session):
    production_task = create_production_task(session, status="ready")
    task_service = build_generation_task_service(session)
    queued_task = task_service.create_generation_task(production_task.task_id, "mock")
    task_service.get_generation_task(queued_task.task_id)
    completed_task = task_service.get_generation_task(queued_task.task_id)
    result = GenerationResultRepository(session).get_by_generation_task_id(completed_task.task_id)
    assert result is not None
    return production_task, completed_task, result, task_service


def test_generation_result_service_returns_result_detail(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    _, _, result, _ = create_completed_generation_result(session)
    service = GenerationResultService(
        generation_result_repository=GenerationResultRepository(session),
    )

    saved_result = service.get_generation_result(result.id)

    assert saved_result.id == result.id
    assert saved_result.version == 1
    assert saved_result.review_status == "reviewing"

    session.close()


def test_generation_review_service_rejected_flow_creates_new_task_and_new_result_version(
    tmp_path: Path,
) -> None:
    session = build_test_session(tmp_path)
    production_task, _, result, task_service = create_completed_generation_result(session)
    review_service = GenerationReviewService(
        generation_result_repository=GenerationResultRepository(session),
        generation_review_repository=GenerationReviewRepository(session),
        production_repository=ProductionRepository(session),
        generation_task_service=task_service,
    )

    outcome = review_service.review_result(
        result_id=result.id,
        review_status="rejected",
        comment="Need another attempt.",
        reviewer="video_reviewer",
        regenerate=True,
    )

    assert outcome.review.generation_result_id == result.id
    assert outcome.review.review_status == "rejected"
    assert outcome.next_generation_task is not None
    assert outcome.next_generation_task.production_task_id == production_task.task_id
    assert outcome.next_generation_task.task_id != result.generation_task_id

    task_service.get_generation_task(outcome.next_generation_task.task_id)
    completed_retry_task = task_service.get_generation_task(outcome.next_generation_task.task_id)
    new_result = GenerationResultRepository(session).get_by_generation_task_id(completed_retry_task.task_id)
    all_tasks = GenerationTaskRepository(session).list_by_production_task_id(production_task.task_id)

    assert new_result is not None
    assert new_result.version == 2
    assert new_result.id != result.id
    assert GenerationResultRepository(session).get_by_id(result.id).review_status == "rejected"
    assert len(all_tasks) == 2

    session.close()
