"""Generation review ORM model."""

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class GenerationReview(Base, IdMixin, TimestampMixin):
    """Represent a review record for a generated video result."""

    __tablename__ = "generation_reviews"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=IdMixin.generate_id)
    generation_result_id: Mapped[str] = mapped_column(
        ForeignKey("generation_results.id"),
        nullable=False,
    )
    review_status: Mapped[str] = mapped_column(String(50), default="reviewing")
    comment: Mapped[str] = mapped_column(Text, default="")
    reviewer: Mapped[str] = mapped_column(String(100), default="")

    generation_result: Mapped["GenerationResult"] = relationship(back_populates="reviews")
