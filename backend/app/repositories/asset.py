"""Asset repository."""

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
