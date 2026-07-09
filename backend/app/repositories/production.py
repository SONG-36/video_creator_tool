"""Production task repository."""

from sqlalchemy import select

from app.models.production_task import ProductionTask
from app.repositories.base import BaseRepository


class ProductionRepository(BaseRepository[ProductionTask]):
    """Data access for production tasks."""

    model = ProductionTask
    id_field = "task_id"

    def list_by_shot_id(self, shot_id: str) -> list[ProductionTask]:
        statement = select(self.model).where(self.model.shot_id == shot_id)
        return list(self.session.scalars(statement).all())
