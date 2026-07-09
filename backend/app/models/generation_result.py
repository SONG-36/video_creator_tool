"""Generation result ORM model."""

from __future__ import annotations

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin, UpdatedTimestampMixin


class GenerationResult(Base, IdMixin, TimestampMixin, UpdatedTimestampMixin):
    """Represent a structured video result produced by a generation task."""

    __tablename__ = "generation_results"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=IdMixin.generate_id)
    generation_task_id: Mapped[str] = mapped_column(
        ForeignKey("generation_tasks.task_id"),
        nullable=False,
    )
    video_url: Mapped[str] = mapped_column(String(500), default="")
    video_path: Mapped[str] = mapped_column(String(500), default="")
    thumbnail_url: Mapped[str] = mapped_column(String(500), default="")
    version: Mapped[int] = mapped_column(default=1)
    generation_cost: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[str] = mapped_column(String(50), default="completed")
    review_status: Mapped[str] = mapped_column(String(50), default="reviewing")

    generation_task: Mapped["GenerationTask"] = relationship(back_populates="generation_results")
    reviews: Mapped[list["GenerationReview"]] = relationship(
        back_populates="generation_result",
        cascade="all, delete-orphan",
    )
