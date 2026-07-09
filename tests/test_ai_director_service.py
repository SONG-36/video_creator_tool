"""AI director service tests."""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models.project import Project
from app.models.script import Script
from app.models.shot import Shot
from app.models.storyboard import Storyboard
from app.providers.director_provider import DirectorPlanResult
from app.repositories.asset import AssetRepository
from app.repositories.production import ProductionRepository
from app.repositories.shot import ShotRepository
from app.services.director import AIDirectorService, InvalidProductionPlanRequestError


class FakeDirectorProvider:
    def generate_plan(self, shot: Shot) -> DirectorPlanResult:
        assert shot.production_type == "ai_generate"
        return DirectorPlanResult.model_validate(
            {
                "generation_mode": "i2v",
                "prompt": "Hero product on sink counter, slow push-in, warm key light.",
                "negative_prompt": "blur, deformation, extra hands",
                "camera": "Slow push-in from medium to close-up.",
                "motion": "Foam spreads across the stain and dissolves it in one pass.",
                "lighting": "Warm window key with cool reflective fill.",
                "asset_requirement": [
                    {
                        "asset_type": "reference_video",
                        "role": "motion_reference",
                        "reference_tag": "@Video1",
                        "requirement_note": "Provide scrubbing motion timing reference.",
                    },
                    {
                        "asset_type": "product_image",
                        "role": "identity_reference",
                        "reference_tag": "@Image1",
                        "requirement_note": "Provide the product packshot for identity lock.",
                    },
                ],
            }
        )


def build_test_session(tmp_path: Path) -> Session:
    database_path = tmp_path / "ai-director-service.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
    return session_factory()


def create_shot(session: Session, production_type: str) -> Shot:
    project = Project(name="Project Director", product_name="Cleaner", video_goal="Product demo")
    script = Script(project=project, content="Show stain, then demonstrate a fast clean.")
    storyboard = Storyboard(script=script)
    shot = Shot(
        storyboard=storyboard,
        shot_number=1,
        time_start=0,
        time_end=5,
        scene="Kitchen sink",
        purpose="Demonstrate cleaning effect",
        action="Foam removes the stain in one motion",
        camera="Medium push-in",
        review_status="approved",
        production_type=production_type,
    )
    session.add(project)
    session.commit()
    return shot


def test_ai_generate_shot_creates_production_task_and_asset_requirements(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    shot = create_shot(session, production_type="ai_generate")
    service = AIDirectorService(
        shot_repository=ShotRepository(session),
        production_repository=ProductionRepository(session),
        asset_repository=AssetRepository(session),
        provider=FakeDirectorProvider(),
    )

    production_task = service.generate_production_plan(shot.shot_id)
    saved_task = ProductionRepository(session).get_by_id(production_task.task_id)
    saved_assets = AssetRepository(session).list_by_production_task_id(production_task.task_id)

    assert saved_task is not None
    assert saved_task.generation_mode == "i2v"
    assert saved_task.prompt
    assert saved_task.negative_prompt == "blur, deformation, extra hands"
    assert saved_task.camera == "Slow push-in from medium to close-up."
    assert saved_task.motion.startswith("Foam spreads")
    assert saved_task.lighting.startswith("Warm window key")
    assert saved_task.status == "waiting_asset"
    assert len(saved_assets) == 2
    saved_asset_map = {asset.role: asset for asset in saved_assets}
    assert saved_asset_map["motion_reference"].shot_id == shot.shot_id
    assert saved_asset_map["motion_reference"].production_task_id == production_task.task_id
    assert saved_asset_map["motion_reference"].reference_tag == "@Video1"
    assert (
        saved_asset_map["motion_reference"].requirement_note
        == "Provide scrubbing motion timing reference."
    )
    assert saved_asset_map["identity_reference"].reference_tag == "@Image1"

    session.close()


def test_real_shoot_cannot_generate_ai_production_plan(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    shot = create_shot(session, production_type="real_shoot")
    service = AIDirectorService(
        shot_repository=ShotRepository(session),
        production_repository=ProductionRepository(session),
        asset_repository=AssetRepository(session),
        provider=FakeDirectorProvider(),
    )

    try:
        service.generate_production_plan(shot.shot_id)
        assert False, "Expected InvalidProductionPlanRequestError"
    except InvalidProductionPlanRequestError as exc:
        assert "production_type ai_generate" in str(exc)

    saved_tasks = ProductionRepository(session).list_by_shot_id(shot.shot_id)
    assert saved_tasks == []

    session.close()
