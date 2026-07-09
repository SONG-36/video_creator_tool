"""Generation task ORM model."""

from __future__ import annotations

from typing import Any, Optional

from sqlalchemy import ForeignKey, JSON, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin, UpdatedTimestampMixin


class GenerationTask(Base, IdMixin, TimestampMixin, UpdatedTimestampMixin):
    """Represent an asynchronous video generation job."""

    __tablename__ = "generation_tasks"

    task_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=IdMixin.generate_id)
    production_task_id: Mapped[str] = mapped_column(
        ForeignKey("production_tasks.task_id"),
        nullable=False,
    )
    provider: Mapped[str] = mapped_column(String(50), default="mock")
    status: Mapped[str] = mapped_column(String(50), default="pending")
    request_payload: Mapped[dict[str, Any]] = mapped_column(JSON, default=dict)
    result_payload: Mapped[Optional[dict[str, Any]]] = mapped_column(JSON, nullable=True)
    error_message: Mapped[str] = mapped_column(Text, default="")

    production_task: Mapped["ProductionTask"] = relationship(back_populates="generation_tasks")
