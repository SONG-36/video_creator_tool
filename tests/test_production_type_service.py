"""Production type service tests."""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models.project import Project
from app.models.script import Script
from app.models.shot import Shot
from app.models.storyboard import Storyboard
from app.repositories.shot import ShotRepository
from app.services.production_type import (
    InvalidProductionTypeSelectionError,
    ProductionTypeService,
)


def build_test_session(tmp_path: Path) -> Session:
    database_path = tmp_path / "production-type-service.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
    return session_factory()


def create_shot(session: Session, review_status: str = "approved") -> Shot:
    project = Project(name="Project Production", product_name="Cleaner", video_goal="Ad")
    script = Script(project=project, content="Select production type")
    storyboard = Storyboard(script=script)
    shot = Shot(
        storyboard=storyboard,
        shot_number=1,
        time_start=0,
        time_end=3,
        scene="Counter top",
        purpose="Introduce the scene",
        action="Camera holds steady",
        camera="Medium static",
        review_status=review_status,
    )
    session.add(project)
    session.commit()
    return shot


def test_approved_shot_can_select_ai_generate(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    shot = create_shot(session, review_status="approved")
    service = ProductionTypeService(shot_repository=ShotRepository(session))

    updated_shot = service.select_production_type(shot_id=shot.shot_id, production_type="ai_generate")

    assert updated_shot.production_type == "ai_generate"
    assert updated_shot.review_status == "approved"
    session.close()


def test_unreviewed_shot_cannot_select_production_type(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    shot = create_shot(session, review_status="waiting_review")
    service = ProductionTypeService(shot_repository=ShotRepository(session))

    try:
        service.select_production_type(shot_id=shot.shot_id, production_type="real_shoot")
        assert False, "Expected InvalidProductionTypeSelectionError"
    except InvalidProductionTypeSelectionError as exc:
        assert "Only approved shots can select a production type." in str(exc)

    unchanged_shot = ShotRepository(session).get_by_id(shot.shot_id)
    assert unchanged_shot is not None
    assert unchanged_shot.production_type == "pending"
    session.close()


def test_invalid_production_type_is_rejected(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    shot = create_shot(session, review_status="approved")
    service = ProductionTypeService(shot_repository=ShotRepository(session))

    try:
        service.select_production_type(shot_id=shot.shot_id, production_type="invalid_type")
        assert False, "Expected InvalidProductionTypeSelectionError"
    except InvalidProductionTypeSelectionError as exc:
        assert "Unsupported production_type" in str(exc)

    session.close()
