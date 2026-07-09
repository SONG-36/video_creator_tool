"""Production task ORM model."""

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class ProductionTask(Base, IdMixin, TimestampMixin):
    """Represent an AI generation task for a shot."""

    __tablename__ = "production_tasks"

    task_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=IdMixin.generate_id)
    shot_id: Mapped[str] = mapped_column(ForeignKey("shots.shot_id"), nullable=False)
    model: Mapped[str] = mapped_column(String(50), default="seedance")
    generation_mode: Mapped[str] = mapped_column(String(50), default="i2v")
    prompt: Mapped[str] = mapped_column(Text, default="")
    negative_prompt: Mapped[str] = mapped_column(Text, default="")
    camera: Mapped[str] = mapped_column(Text, default="")
    motion: Mapped[str] = mapped_column(Text, default="")
    lighting: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(50), default="draft")

    shot: Mapped["Shot"] = relationship(back_populates="production_tasks")
    assets: Mapped[list["Asset"]] = relationship(back_populates="production_task")
    generation_tasks: Mapped[list["GenerationTask"]] = relationship(
        back_populates="production_task",
        cascade="all, delete-orphan",
    )
