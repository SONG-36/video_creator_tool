"""Script API tests."""

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.api.dependencies import get_script_service
from app.db.base import Base
from app.main import app
from app.models.project import Project
from app.repositories.project import ProjectRepository
from app.repositories.script import ScriptRepository
from app.services.script import ScriptService


def build_test_session(tmp_path: Path) -> Session:
    database_path = tmp_path / "scripts-api.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
    return session_factory()


def build_script_service(session: Session) -> ScriptService:
    return ScriptService(
        project_repository=ProjectRepository(session),
        script_repository=ScriptRepository(session),
    )


def test_create_and_get_script_api_with_project_association(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    project = Project(
        name="Project API",
        product_name="Spray",
        video_goal="TikTok demo",
    )
    session.add(project)
    session.commit()

    app.dependency_overrides[get_script_service] = lambda: build_script_service(session)
    client = TestClient(app)

    create_response = client.post(
        f"/projects/{project.project_id}/scripts",
        json={"content": "Clean the sink with one spray.", "created_by": "writer_api"},
    )

    assert create_response.status_code == 200
    create_body = create_response.json()
    script_data = create_body["data"]["script"]

    assert script_data["project_id"] == project.project_id
    assert script_data["version"] == 1
    assert script_data["content"] == "Clean the sink with one spray."

    get_response = client.get(f"/scripts/{script_data['script_id']}")

    assert get_response.status_code == 200
    get_body = get_response.json()

    assert get_body["data"]["script"]["script_id"] == script_data["script_id"]
    assert get_body["data"]["script"]["project_id"] == project.project_id
    assert get_body["data"]["script"]["created_by"] == "writer_api"

    version_response = client.post(
        f"/projects/{project.project_id}/scripts",
        json={"content": "Updated sink script."},
    )

    assert version_response.status_code == 200
    assert version_response.json()["data"]["script"]["version"] == 2

    app.dependency_overrides.clear()
    session.close()
