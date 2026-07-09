"""Storyboard repository."""

from sqlalchemy import select

from app.models.storyboard import Storyboard
from app.repositories.base import BaseRepository


class StoryboardRepository(BaseRepository[Storyboard]):
    """Data access for storyboards."""

    model = Storyboard
    id_field = "storyboard_id"

    def list_by_script_id(self, script_id: str) -> list[Storyboard]:
        statement = select(self.model).where(self.model.script_id == script_id)
        return list(self.session.scalars(statement).all())
