"""Asset API tests."""

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import get_asset_service
from app.db.base import Base
from app.main import app
from app.models.asset import Asset
from app.models.production_task import ProductionTask
from app.models.project import Project
from app.models.script import Script
from app.models.shot import Shot
from app.models.storyboard import Storyboard
from app.repositories.asset import AssetRepository
from app.repositories.production import ProductionRepository
from app.services.asset import AssetService


def build_test_session(tmp_path: Path) -> Session:
    database_path = tmp_path / "asset-api.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
    return session_factory()


def create_production_task_with_asset_requirement(session: Session) -> tuple[ProductionTask, Asset]:
    project = Project(name="Project Asset API", product_name="Soap", video_goal="Ad")
    script = Script(project=project, content="Need product image and motion video.")
    storyboard = Storyboard(script=script)
    shot = Shot(
        storyboard=storyboard,
        shot_number=1,
        time_start=0,
        time_end=4,
        scene="Countertop",
        purpose="Prepare asset upload",
        action="Collect references",
        camera="Front medium",
        production_type="ai_generate",
        review_status="approved",
    )
    production_task = ProductionTask(
        shot=shot,
        status="waiting_asset",
        generation_mode="i2v",
        prompt="Prepare first frame and motion references.",
    )
    asset = Asset(
        shot=shot,
        production_task=production_task,
        asset_type="product_image",
        role="identity_reference",
        reference_tag="@Image1",
        requirement_note="Provide hero product packshot.",
        status="pending",
    )
    session.add(project)
    session.commit()
    return production_task, asset


def build_asset_service(session: Session, storage_dir: Path) -> AssetService:
    return AssetService(
        asset_repository=AssetRepository(session),
        production_repository=ProductionRepository(session),
        storage_dir=storage_dir,
    )


def test_asset_upload_list_and_status_update_api(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    production_task, asset_requirement = create_production_task_with_asset_requirement(session)

    app.dependency_overrides[get_asset_service] = lambda: build_asset_service(
        session,
        tmp_path / "uploads",
    )
    client = TestClient(app)

    upload_response = client.post(
        "/assets/upload",
        data={
            "production_task_id": production_task.task_id,
            "role": asset_requirement.role,
            "reference_tag": asset_requirement.reference_tag,
            "requirement_note": "Provide hero product packshot.",
        },
        files={"file": ("product.png", b"fake-image-bytes", "image/png")},
    )

    assert upload_response.status_code == 200
    uploaded_asset = upload_response.json()["data"]["asset"]
    assert uploaded_asset["production_task_id"] == production_task.task_id
    assert uploaded_asset["role"] == "identity_reference"
    assert uploaded_asset["reference_tag"] == "@Image1"
    assert uploaded_asset["status"] == "uploaded"
    assert uploaded_asset["file_name"].endswith("product.png")

    list_response = client.get(f"/production-tasks/{production_task.task_id}/assets")
    assert list_response.status_code == 200
    listed_assets = list_response.json()["data"]["assets"]["assets"]
    assert len(listed_assets) == 1
    assert listed_assets[0]["asset_id"] == uploaded_asset["asset_id"]

    status_response = client.patch(
        f"/assets/{uploaded_asset['asset_id']}/status",
        json={"status": "approved"},
    )
    assert status_response.status_code == 200
    assert status_response.json()["data"]["asset"]["status"] == "approved"

    saved_task = ProductionRepository(session).get_by_id(production_task.task_id)
    assert saved_task is not None
    assert saved_task.status == "ready"

    app.dependency_overrides.clear()
    session.close()
