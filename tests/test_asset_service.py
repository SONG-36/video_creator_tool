"""Asset service tests."""

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
from app.repositories.asset import AssetRepository
from app.repositories.production import ProductionRepository
from app.services.asset import AssetService


def build_test_session(tmp_path: Path) -> Session:
    database_path = tmp_path / "asset-service.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
    return session_factory()


def create_production_task_with_asset_requirement(session: Session) -> tuple[ProductionTask, Asset]:
    project = Project(name="Project Asset", product_name="Cleaner", video_goal="Demo")
    script = Script(project=project, content="Upload source materials.")
    storyboard = Storyboard(script=script)
    shot = Shot(
        storyboard=storyboard,
        shot_number=1,
        time_start=0,
        time_end=3,
        scene="Sink edge",
        purpose="Reference upload",
        action="Prepare upload references",
        camera="Static medium",
        production_type="ai_generate",
        review_status="approved",
    )
    production_task = ProductionTask(
        shot=shot,
        status="waiting_asset",
        generation_mode="r2v",
        prompt="Use references for motion and identity.",
    )
    asset = Asset(
        shot=shot,
        production_task=production_task,
        asset_type="reference_video",
        role="motion_reference",
        reference_tag="@Video1",
        requirement_note="Provide motion timing reference.",
        status="pending",
    )
    session.add(project)
    session.commit()
    return production_task, asset


def test_asset_service_upload_list_and_status_update(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    production_task, asset_requirement = create_production_task_with_asset_requirement(session)
    service = AssetService(
        asset_repository=AssetRepository(session),
        production_repository=ProductionRepository(session),
        storage_dir=tmp_path / "uploads",
    )

    uploaded_asset = service.upload_asset(
        production_task_id=production_task.task_id,
        role=asset_requirement.role,
        reference_tag=asset_requirement.reference_tag,
        requirement_note=asset_requirement.requirement_note,
        filename="motion-reference.mp4",
        content=b"fake-video-bytes",
        content_type="video/mp4",
    )

    assert uploaded_asset.asset_id == asset_requirement.asset_id
    assert uploaded_asset.production_task_id == production_task.task_id
    assert uploaded_asset.status == "uploaded"
    assert Path(uploaded_asset.file_path).exists()

    assets = service.list_assets(production_task.task_id)
    assert len(assets) == 1
    assert assets[0].role == "motion_reference"
    assert assets[0].reference_tag == "@Video1"

    approved_asset = service.update_asset_status(uploaded_asset.asset_id, "approved")
    refreshed_task = ProductionRepository(session).get_by_id(production_task.task_id)

    assert approved_asset.status == "approved"
    assert refreshed_task is not None
    assert refreshed_task.status == "ready"

    session.close()
