"""Generation task API tests."""

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import get_generation_task_service
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
from app.repositories.generation_task import GenerationTaskRepository
from app.repositories.production import ProductionRepository
from app.services.generation_task import GenerationTaskService, VideoProviderRegistry


def build_test_session(tmp_path: Path) -> Session:
    database_path = tmp_path / "generation-task-api.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
    return session_factory()


def create_production_task(session: Session, status: str = "ready") -> ProductionTask:
    project = Project(name="Project Generation API", product_name="Soap", video_goal="Ad")
    script = Script(project=project, content="Create a generated ad clip.")
    storyboard = Storyboard(script=script)
    shot = Shot(
        storyboard=storyboard,
        shot_number=1,
        time_start=0,
        time_end=5,
        scene="Countertop hero shot",
        purpose="Generate final hero video",
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


def build_service(session: Session) -> GenerationTaskService:
    return GenerationTaskService(
        generation_task_repository=GenerationTaskRepository(session),
        generation_result_repository=GenerationResultRepository(session),
        production_repository=ProductionRepository(session),
        asset_repository=AssetRepository(session),
        provider_registry=VideoProviderRegistry(providers={"mock": MockVideoProvider()}),
    )


def test_generation_task_api_create_and_query_flow(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    production_task = create_production_task(session, status="ready")

    app.dependency_overrides[get_generation_task_service] = lambda: build_service(session)
    client = TestClient(app)

    create_response = client.post(
        "/generation/tasks",
        json={"production_task_id": production_task.task_id, "provider": "mock"},
    )
    assert create_response.status_code == 200
    task_data = create_response.json()["data"]["task"]
    assert task_data["production_task_id"] == production_task.task_id
    assert task_data["status"] == "queued"

    running_response = client.get(f"/generation/tasks/{task_data['task_id']}")
    assert running_response.status_code == 200
    assert running_response.json()["data"]["task"]["status"] == "running"

    completed_response = client.get(f"/generation/tasks/{task_data['task_id']}")
    assert completed_response.status_code == 200
    completed_task = completed_response.json()["data"]["task"]
    assert completed_task["status"] == "completed"
    assert completed_task["result_payload"]["video_path"].endswith(f"{task_data['task_id']}.mp4")
    generation_result = GenerationResultRepository(session).get_by_generation_task_id(
        task_data["task_id"]
    )
    assert generation_result is not None
    assert generation_result.version == 1

    saved_production_task = ProductionRepository(session).get_by_id(production_task.task_id)
    assert saved_production_task is not None
    assert saved_production_task.status == "completed"

    app.dependency_overrides.clear()
    session.close()


def test_generation_task_api_rejects_non_ready_production_task(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    production_task = create_production_task(session, status="waiting_asset")

    app.dependency_overrides[get_generation_task_service] = lambda: build_service(session)
    client = TestClient(app)

    response = client.post(
        "/generation/tasks",
        json={"production_task_id": production_task.task_id, "provider": "mock"},
    )

    assert response.status_code == 400
    assert "status ready" in response.json()["detail"]

    app.dependency_overrides.clear()
    session.close()
