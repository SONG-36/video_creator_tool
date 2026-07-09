"""Script service tests."""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models.project import Project
from app.repositories.project import ProjectRepository
from app.repositories.script import ScriptRepository
from app.services.script import ScriptService


def build_test_session(tmp_path: Path) -> Session:
    database_path = tmp_path / "script-service.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
    return session_factory()


def test_script_service_creates_and_versions_scripts(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    project = Project(name="Project S", product_name="Soap", video_goal="Video")
    session.add(project)
    session.commit()

    service = ScriptService(
        project_repository=ProjectRepository(session),
        script_repository=ScriptRepository(session),
    )

    first_script = service.create_script(
        project_id=project.project_id,
        content="First version",
        created_by="writer_1",
    )
    second_script = service.save_script_version(
        script_id=first_script.script_id,
        content="Second version",
    )

    assert first_script.version == 1
    assert second_script.project_id == project.project_id
    assert second_script.version == 2
    assert service.get_script(second_script.script_id).content == "Second version"

    session.close()
