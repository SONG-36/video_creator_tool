"""Generation review repository."""

from sqlalchemy import select

from app.models.generation_review import GenerationReview
from app.repositories.base import BaseRepository


class GenerationReviewRepository(BaseRepository[GenerationReview]):
    """Data access for generation result review records."""

    model = GenerationReview
    id_field = "id"

    def list_by_generation_result_id(self, generation_result_id: str) -> list[GenerationReview]:
        statement = select(self.model).where(self.model.generation_result_id == generation_result_id)
        return list(self.session.scalars(statement).all())
