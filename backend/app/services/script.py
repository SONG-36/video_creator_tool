"""Script service."""

from dataclasses import dataclass
from typing import Optional

from app.models.script import Script
from app.repositories.project import ProjectRepository
from app.repositories.script import ScriptRepository


class ProjectNotFoundError(Exception):
    """Raised when a script is created for a missing project."""


class ScriptNotFoundError(Exception):
    """Raised when a requested script does not exist."""


@dataclass
class ScriptService:
    """Provide script management using repositories only."""

    project_repository: ProjectRepository
    script_repository: ScriptRepository

    def create_script(self, project_id: str, content: str, created_by: Optional[str] = None) -> Script:
        project = self.project_repository.get_by_id(project_id)
        if project is None:
            raise ProjectNotFoundError(f"Project {project_id} not found.")

        existing_scripts = self.script_repository.list_by_project_id(project_id)
        next_version = max((script.version for script in existing_scripts), default=0) + 1

        return self.script_repository.create(
            project_id=project_id,
            content=content,
            version=next_version,
            created_by=created_by,
        )

    def save_script_version(self, script_id: str, content: str, created_by: Optional[str] = None) -> Script:
        existing_script = self.script_repository.get_by_id(script_id)
        if existing_script is None:
            raise ScriptNotFoundError(f"Script {script_id} not found.")

        return self.create_script(
            project_id=existing_script.project_id,
            content=content,
            created_by=created_by or existing_script.created_by,
        )

    def get_script(self, script_id: str) -> Script:
        script = self.script_repository.get_by_id(script_id)
        if script is None:
            raise ScriptNotFoundError(f"Script {script_id} not found.")

        return script
