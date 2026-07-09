"""Repository CRUD tests."""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models import Project, Script, Shot, Storyboard
from app.repositories import (
    AssetRepository,
    ProductionRepository,
    ProjectRepository,
    ScriptRepository,
    ShotRepository,
)


def build_test_session(tmp_path: Path) -> Session:
    database_path = tmp_path / "repositories.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
    return session_factory()


def test_project_repository_create_query_update_delete(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    repository = ProjectRepository(session)

    project = repository.create(
        name="Project A",
        product_name="Cleaner",
        video_goal="Launch video",
    )

    fetched = repository.get_by_id(project.project_id)
    updated = repository.update(project.project_id, name="Project A Updated")
    deleted = repository.delete(project.project_id)

    assert fetched is not None
    assert fetched.product_name == "Cleaner"
    assert updated is not None
    assert updated.name == "Project A Updated"
    assert deleted is True
    assert repository.get_by_id(project.project_id) is None

    session.close()


def test_script_repository_create_query_and_update(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    project = Project(name="Project B", product_name="Steam Cleaner", video_goal="Demo")
    session.add(project)
    session.commit()

    repository = ScriptRepository(session)
    script = repository.create(
        project_id=project.project_id,
        content="Original script",
        created_by="writer_1",
    )

    scripts = repository.list_by_project_id(project.project_id)
    updated = repository.update(script.script_id, content="Updated script", version=2)

    assert len(scripts) == 1
    assert scripts[0].script_id == script.script_id
    assert updated is not None
    assert updated.content == "Updated script"
    assert updated.version == 2

    session.close()


def test_shot_asset_and_production_repositories_crud(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    project = Project(name="Project C", product_name="Brush", video_goal="Ad clip")
    script = Script(project=project, content="Scene list")
    storyboard = Storyboard(script=script)
    session.add(project)
    session.commit()

    shot_repository = ShotRepository(session)
    asset_repository = AssetRepository(session)
    production_repository = ProductionRepository(session)

    shot = shot_repository.create(
        storyboard_id=storyboard.storyboard_id,
        shot_number=1,
        time_start=0,
        time_end=3,
        scene="Kitchen counter",
        purpose="Introduce the stain",
        action="Pan across surface",
        camera="Wide pan",
    )
    task = production_repository.create(
        shot_id=shot.shot_id,
        prompt="Clean the counter",
        negative_prompt="low quality",
        camera="Slow dolly-in",
        motion="Foam spreads from left to right",
        lighting="Bright commercial kitchen light",
    )
    asset = asset_repository.create(
        shot_id=shot.shot_id,
        production_task_id=task.task_id,
        asset_type="reference_image",
        role="first_frame",
        reference_tag="@Image1",
        requirement_note="Use as the opening frame reference",
        file_path="storage/assets/counter.png",
    )

    shots = shot_repository.list_by_storyboard_id(storyboard.storyboard_id)
    assets = asset_repository.list_by_shot_id(shot.shot_id)
    tasks = production_repository.list_by_shot_id(shot.shot_id)
    task_assets = asset_repository.list_by_production_task_id(task.task_id)
    updated_shot = shot_repository.update(shot.shot_id, production_type="ai_generate")
    updated_asset = asset_repository.update(asset.asset_id, status="uploaded")
    updated_task = production_repository.update(task.task_id, status="ready")

    assert len(shots) == 1
    assert shots[0].scene == "Kitchen counter"
    assert len(assets) == 1
    assert assets[0].file_path.endswith("counter.png")
    assert assets[0].reference_tag == "@Image1"
    assert len(tasks) == 1
    assert tasks[0].model == "seedance"
    assert tasks[0].camera == "Slow dolly-in"
    assert len(task_assets) == 1
    assert task_assets[0].role == "first_frame"
    assert updated_shot is not None
    assert updated_shot.production_type == "ai_generate"
    assert updated_asset is not None
    assert updated_asset.status == "uploaded"
    assert updated_task is not None
    assert updated_task.status == "ready"

    session.close()
