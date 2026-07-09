"""Generation result API tests."""

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import get_generation_result_service, get_generation_review_service
from app.db.base import Base
from app.main import app
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
    database_path = tmp_path / "generation-result-api.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
    return session_factory()


def create_production_task(session: Session, status: str = "ready") -> ProductionTask:
    project = Project(name="Project Video Review API", product_name="Soap", video_goal="Ad")
    script = Script(project=project, content="Review the generated clip.")
    storyboard = Storyboard(script=script)
    shot = Shot(
        storyboard=storyboard,
        shot_number=1,
        time_start=0,
        time_end=5,
        scene="Countertop hero shot",
        purpose="Review generated result",
        action="Bottle glides in and wipe clears surface",
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


def build_generation_result_service(session: Session) -> GenerationResultService:
    return GenerationResultService(
        generation_result_repository=GenerationResultRepository(session),
    )


def build_generation_review_service(session: Session) -> GenerationReviewService:
    return GenerationReviewService(
        generation_result_repository=GenerationResultRepository(session),
        generation_review_repository=GenerationReviewRepository(session),
        production_repository=ProductionRepository(session),
        generation_task_service=build_generation_task_service(session),
    )


def create_completed_generation_result(session: Session):
    production_task = create_production_task(session, status="ready")
    task_service = build_generation_task_service(session)
    queued_task = task_service.create_generation_task(production_task.task_id, "mock")
    task_service.get_generation_task(queued_task.task_id)
    completed_task = task_service.get_generation_task(queued_task.task_id)
    result = GenerationResultRepository(session).get_by_generation_task_id(completed_task.task_id)
    assert result is not None
    return production_task, completed_task, result


def test_generation_result_api_get_result_detail(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    _, _, result = create_completed_generation_result(session)

    app.dependency_overrides[get_generation_result_service] = lambda: build_generation_result_service(session)
    client = TestClient(app)

    response = client.get(f"/generation-results/{result.id}")

    assert response.status_code == 200
    result_data = response.json()["data"]["result"]
    assert result_data["result_id"] == result.id
    assert result_data["prompt"] == "Create a polished hero shot from approved references."
    assert result_data["version"] == 1

    app.dependency_overrides.clear()
    session.close()


def test_generation_result_api_review_and_regenerate_with_prompt_override(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    production_task, _, result = create_completed_generation_result(session)

    app.dependency_overrides[get_generation_result_service] = lambda: build_generation_result_service(session)
    app.dependency_overrides[get_generation_review_service] = lambda: build_generation_review_service(session)
    client = TestClient(app)

    review_response = client.post(
        f"/generation-results/{result.id}/review",
        json={
            "review_status": "revision_required",
            "comment": "Please tighten the hook and reframe the open.",
            "reviewer": "video_reviewer",
            "regenerate": True,
            "prompt_override": "Create a tighter hook shot with a faster opening move.",
        },
    )

    assert review_response.status_code == 200
    review_data = review_response.json()["data"]["review"]
    assert review_data["review"]["review_status"] == "revision_required"
    assert review_data["next_generation_task"] is not None
    next_task_id = review_data["next_generation_task"]["task_id"]

    latest_task = GenerationTaskRepository(session).get_by_id(next_task_id)
    assert latest_task is not None
    assert latest_task.request_payload["prompt"] == "Create a tighter hook shot with a faster opening move."

    task_service = build_generation_task_service(session)
    task_service.get_generation_task(next_task_id)
    completed_retry_task = task_service.get_generation_task(next_task_id)
    latest_result = GenerationResultRepository(session).get_by_generation_task_id(completed_retry_task.task_id)

    assert latest_result is not None
    assert latest_result.version == 2
    assert latest_result.generation_task.production_task_id == production_task.task_id
    assert GenerationResultRepository(session).get_by_id(result.id).review_status == "revision_required"

    app.dependency_overrides.clear()
    session.close()
