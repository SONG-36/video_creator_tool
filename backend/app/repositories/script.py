"""Script repository."""

from sqlalchemy import select

from app.models.script import Script
from app.repositories.base import BaseRepository


class ScriptRepository(BaseRepository[Script]):
    """Data access for scripts."""

    model = Script
    id_field = "script_id"

    def list_by_project_id(self, project_id: str) -> list[Script]:
        statement = select(self.model).where(self.model.project_id == project_id)
        return list(self.session.scalars(statement).all())
