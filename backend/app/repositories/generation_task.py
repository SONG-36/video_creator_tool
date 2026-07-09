"""Generation task repository."""

from typing import Optional

from sqlalchemy import select

from app.models.generation_task import GenerationTask
from app.repositories.base import BaseRepository


class GenerationTaskRepository(BaseRepository[GenerationTask]):
    """Data access for asynchronous generation tasks."""

    model = GenerationTask
    id_field = "task_id"

    def list_by_production_task_id(self, production_task_id: str) -> list[GenerationTask]:
        statement = select(self.model).where(self.model.production_task_id == production_task_id)
        return list(self.session.scalars(statement).all())

    def get_latest_by_production_task_id(self, production_task_id: str) -> Optional[GenerationTask]:
        statement = (
            select(self.model)
            .where(self.model.production_task_id == production_task_id)
            .order_by(self.model.created_at.desc())
            .limit(1)
        )
        return self.session.scalar(statement)
