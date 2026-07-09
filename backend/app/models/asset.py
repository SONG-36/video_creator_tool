"""Asset ORM model."""

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.models.mixins import IdMixin


class Asset(Base, IdMixin):
    """Represent an asset required for AI production."""

    __tablename__ = "assets"

    asset_id: Mapped[str] = mapped_column(String(36), primary_key=True, default=IdMixin.generate_id)
    shot_id: Mapped[str] = mapped_column(ForeignKey("shots.shot_id"), nullable=False)
    asset_type: Mapped[str] = mapped_column(String(50))
    file_path: Mapped[str] = mapped_column(String(500))
    status: Mapped[str] = mapped_column(String(50), default="required")

    shot: Mapped["Shot"] = relationship(back_populates="assets")
