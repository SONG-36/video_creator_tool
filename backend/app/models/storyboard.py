"""Storyboard ORM model."""

from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin


class Storyboard(Base, IdMixin):
    """Represent an AI-generated storyboard."""

    __tablename__ = "storyboards"

    storyboard_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=IdMixin.generate_id)
    script_id: Mapped[str] = mapped_column(ForeignKey("scripts.script_id"), nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(50), default="draft")

    script: Mapped["Script"] = relationship(back_populates="storyboards")
    shots: Mapped[list["Shot"]] = relationship(
        back_populates="storyboard",
        cascade="all, delete-orphan",
    )
