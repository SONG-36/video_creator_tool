"""Shot repository."""

from sqlalchemy import select

from app.models.shot import Shot
from app.repositories.base import BaseRepository


class ShotRepository(BaseRepository[Shot]):
    """Data access for shots."""

    model = Shot
    id_field = "shot_id"

    def list_by_storyboard_id(self, storyboard_id: str) -> list[Shot]:
        statement = select(self.model).where(self.model.storyboard_id == storyboard_id)
        return list(self.session.scalars(statement).all())
