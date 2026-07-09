"""Generation result repository."""

from typing import Optional

from sqlalchemy import func, select

from app.models.generation_result import GenerationResult
from app.models.generation_task import GenerationTask
from app.repositories.base import BaseRepository


class GenerationResultRepository(BaseRepository[GenerationResult]):
    """Data access for structured generation results."""

    model = GenerationResult
    id_field = "id"

    def list_by_generation_task_id(self, generation_task_id: str) -> list[GenerationResult]:
        statement = select(self.model).where(self.model.generation_task_id == generation_task_id)
        return list(self.session.scalars(statement).all())

    def get_by_generation_task_id(self, generation_task_id: str) -> Optional[GenerationResult]:
        statement = select(self.model).where(self.model.generation_task_id == generation_task_id).limit(1)
        return self.session.scalar(statement)

    def get_latest_by_generation_task_id(
        self,
        generation_task_id: str,
    ) -> Optional[GenerationResult]:
        statement = (
            select(self.model)
            .where(self.model.generation_task_id == generation_task_id)
            .order_by(self.model.version.desc(), self.model.created_at.desc())
            .limit(1)
        )
        return self.session.scalar(statement)

    def get_next_version_for_production_task(self, production_task_id: str) -> int:
        statement = (
            select(func.max(self.model.version))
            .join(GenerationTask, GenerationTask.task_id == self.model.generation_task_id)
            .where(GenerationTask.production_task_id == production_task_id)
        )
        current_version = self.session.scalar(statement)
        return int(current_version or 0) + 1
