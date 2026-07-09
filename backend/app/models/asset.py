"""Asset ORM model."""

from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin


class Asset(Base, IdMixin):
    """Represent an asset required for AI production."""

    __tablename__ = "assets"

    asset_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=IdMixin.generate_id)
    shot_id: Mapped[str] = mapped_column(ForeignKey("shots.shot_id"), nullable=False)
    production_task_id: Mapped[Optional[str]] = mapped_column(
        ForeignKey("production_tasks.task_id"),
        nullable=True,
    )
    asset_type: Mapped[str] = mapped_column(String(50))
    role: Mapped[str] = mapped_column(String(100), default="")
    reference_tag: Mapped[str] = mapped_column(String(50), default="")
    requirement_note: Mapped[str] = mapped_column(Text, default="")
    file_path: Mapped[str] = mapped_column(String(500), default="")
    status: Mapped[str] = mapped_column(String(50), default="pending")

    shot: Mapped["Shot"] = relationship(back_populates="assets")
    production_task: Mapped[Optional["ProductionTask"]] = relationship(back_populates="assets")
