"""Shared model mixins."""

from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column


def utc_now() -> datetime:
    """Return a timezone-aware UTC timestamp."""

    return datetime.now(timezone.utc)


class IdMixin:
    """Provide a string primary key."""

    @staticmethod
    def generate_id() -> str:
        return str(uuid4())


class TimestampMixin:
    """Provide standard timestamp columns."""

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)


class UpdatedTimestampMixin:
    """Provide an updated timestamp column."""

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utc_now,
        onupdate=utc_now,
    )


ShortText = String(255)
LongText = Text()
