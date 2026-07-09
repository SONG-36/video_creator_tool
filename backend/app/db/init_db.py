"""Database initialization entrypoint."""

from app.db import session as db_session
from app.db.base import Base
from app.models import (
    Asset,
    GenerationResult,
    GenerationReview,
    GenerationTask,
    ProductionTask,
    Project,
    Script,
    Shot,
    ShotReview,
    Storyboard,
)


def init_database() -> None:
    """Create all configured database tables."""

    Base.metadata.create_all(bind=db_session.engine)


if __name__ == "__main__":
    init_database()
