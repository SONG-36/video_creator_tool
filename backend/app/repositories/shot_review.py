"""Shot review repository."""

from sqlalchemy import select

from app.models.shot_review import ShotReview
from app.repositories.base import BaseRepository


class ShotReviewRepository(BaseRepository[ShotReview]):
    """Data access for shot reviews."""

    model = ShotReview
    id_field = "review_id"

    def list_by_shot_id(self, shot_id: str) -> list[ShotReview]:
        statement = select(self.model).where(self.model.shot_id == shot_id)
        return list(self.session.scalars(statement).all())
