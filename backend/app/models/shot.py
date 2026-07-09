"""Shot ORM model."""

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin


class Shot(Base, IdMixin):
    """Represent a single production shot."""

    __tablename__ = "shots"

    shot_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=IdMixin.generate_id)
    storyboard_id: Mapped[str] = mapped_column(ForeignKey("storyboards.storyboard_id"), nullable=False)
    shot_number: Mapped[int] = mapped_column(Integer)
    time_start: Mapped[int] = mapped_column(Integer)
    time_end: Mapped[int] = mapped_column(Integer)
    scene: Mapped[str] = mapped_column(Text)
    purpose: Mapped[str] = mapped_column(Text)
    action: Mapped[str] = mapped_column(Text)
    camera: Mapped[str] = mapped_column(Text)
    production_type: Mapped[str] = mapped_column(String(50), default="pending")
    review_status: Mapped[str] = mapped_column(String(50), default="waiting_review")

    storyboard: Mapped["Storyboard"] = relationship(back_populates="shots")
    reviews: Mapped[list["ShotReview"]] = relationship(
        back_populates="shot",
        cascade="all, delete-orphan",
    )
    production_tasks: Mapped[list["ProductionTask"]] = relationship(
        back_populates="shot",
        cascade="all, delete-orphan",
    )
    assets: Mapped[list["Asset"]] = relationship(
        back_populates="shot",
        cascade="all, delete-orphan",
    )
