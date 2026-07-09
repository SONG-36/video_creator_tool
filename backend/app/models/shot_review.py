"""Shot review ORM model."""

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class ShotReview(Base, IdMixin, TimestampMixin):
    """Represent a human review record for a shot."""

    __tablename__ = "shot_reviews"

    review_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=IdMixin.generate_id)
    shot_id: Mapped[str] = mapped_column(ForeignKey("shots.shot_id"), nullable=False)
    review_type: Mapped[str] = mapped_column(String(50), default="storyboard")
    result: Mapped[str] = mapped_column(String(50))
    comment: Mapped[str] = mapped_column(Text, default="")
    reviewer: Mapped[str] = mapped_column(String(255), default="")

    shot: Mapped["Shot"] = relationship(back_populates="reviews")
