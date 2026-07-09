"""API dependency providers."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.repositories.project import ProjectRepository
from app.repositories.script import ScriptRepository
from app.services.script import ScriptService


def get_script_service(session: Session = Depends(get_db_session)) -> ScriptService:
    """Build the script service from repository dependencies."""

    project_repository = ProjectRepository(session)
    script_repository = ScriptRepository(session)
    return ScriptService(
        project_repository=project_repository,
        script_repository=script_repository,
    )
