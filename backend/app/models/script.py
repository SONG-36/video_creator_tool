"""Script ORM model."""

from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin


class Script(Base, IdMixin, TimestampMixin):
    """Represent a user-provided script."""

    __tablename__ = "scripts"

    script_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=IdMixin.generate_id)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.project_id"), nullable=False)
    content: Mapped[str] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String(50), default="draft")
    created_by: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    project: Mapped["Project"] = relationship(back_populates="scripts")
    storyboards: Mapped[list["Storyboard"]] = relationship(
        back_populates="script",
        cascade="all, delete-orphan",
    )
