"""Project ORM model."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin, TimestampMixin, UpdatedTimestampMixin


class Project(Base, IdMixin, TimestampMixin, UpdatedTimestampMixin):
    """Represent a video production project."""

    __tablename__ = "projects"

    project_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=IdMixin.generate_id)
    name: Mapped[str] = mapped_column(String(255))
    product_name: Mapped[str] = mapped_column(String(255))
    video_goal: Mapped[str] = mapped_column(String(255))
    status: Mapped[str] = mapped_column(String(50), default="created")

    scripts: Mapped[list["Script"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
