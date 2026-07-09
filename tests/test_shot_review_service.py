"""Shot review service tests."""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.models.project import Project
from app.models.script import Script
from app.models.shot import Shot
from app.models.storyboard import Storyboard
from app.repositories.shot import ShotRepository
from app.repositories.shot_review import ShotReviewRepository
from app.services.review import InvalidShotReviewTransitionError, ShotReviewService


def build_test_session(tmp_path: Path) -> Session:
    database_path = tmp_path / "shot-review-service.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    Base.metadata.create_all(bind=engine)
    session_factory = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
    return session_factory()


def create_shot(session: Session, review_status: str = "waiting_review") -> Shot:
    project = Project(name="Project Review", product_name="Cleaner", video_goal="Ad")
    script = Script(project=project, content="Demo script")
    storyboard = Storyboard(script=script)
    shot = Shot(
        storyboard=storyboard,
        shot_number=1,
        time_start=0,
        time_end=3,
        scene="Dirty sink",
        purpose="Show problem",
        action="Static stain shot",
        camera="Close-up",
        review_status=review_status,
    )
    session.add(project)
    session.commit()
    return shot


def test_waiting_review_to_rejected_succeeds_and_saves_review(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    shot = create_shot(session)
    service = ShotReviewService(
        shot_repository=ShotRepository(session),
        shot_review_repository=ShotReviewRepository(session),
    )

    review = service.review_shot(
        shot_id=shot.shot_id,
        result="rejected",
        comment="Scene is not usable",
        reviewer="qa_1",
    )

    updated_shot = ShotRepository(session).get_by_id(shot.shot_id)
    reviews = ShotReviewRepository(session).list_by_shot_id(shot.shot_id)

    assert updated_shot is not None
    assert updated_shot.review_status == "rejected"
    assert review.shot_id == shot.shot_id
    assert review.result == "rejected"
    assert len(reviews) == 1
    assert reviews[0].comment == "Scene is not usable"
    assert reviews[0].reviewer == "qa_1"

    session.close()


def test_illegal_state_transition_fails(tmp_path: Path) -> None:
    session = build_test_session(tmp_path)
    shot = create_shot(session, review_status="approved")
    service = ShotReviewService(
        shot_repository=ShotRepository(session),
        shot_review_repository=ShotReviewRepository(session),
    )

    try:
        service.review_shot(shot_id=shot.shot_id, result="rejected", comment="too late")
        assert False, "Expected InvalidShotReviewTransitionError"
    except InvalidShotReviewTransitionError as exc:
        assert "Illegal review transition" in str(exc)

    reviews = ShotReviewRepository(session).list_by_shot_id(shot.shot_id)
    assert reviews == []

    session.close()
