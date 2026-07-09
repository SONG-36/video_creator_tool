"""Asset repository."""

from typing import Optional

from sqlalchemy import select

from app.models.asset import Asset
from app.repositories.base import BaseRepository


class AssetRepository(BaseRepository[Asset]):
    """Data access for assets."""

    model = Asset
    id_field = "asset_id"

    def list_by_shot_id(self, shot_id: str) -> list[Asset]:
        statement = select(self.model).where(self.model.shot_id == shot_id)
        return list(self.session.scalars(statement).all())

    def list_by_production_task_id(self, production_task_id: str) -> list[Asset]:
        statement = select(self.model).where(self.model.production_task_id == production_task_id)
        return list(self.session.scalars(statement).all())

    def get_by_task_role_reference(
        self,
        production_task_id: str,
        role: str,
        reference_tag: str,
    ) -> Optional[Asset]:
        statement = select(self.model).where(
            self.model.production_task_id == production_task_id,
            self.model.role == role,
            self.model.reference_tag == reference_tag,
        )
        return self.session.scalar(statement)
