"""Shot repository."""

from typing import Any

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

    def create_many(self, shots_data: list[dict[str, Any]]) -> list[Shot]:
        instances = [self.model(**shot_data) for shot_data in shots_data]
        self.session.add_all(instances)
        self.session.commit()

        for instance in instances:
            self.session.refresh(instance)

        return instances
