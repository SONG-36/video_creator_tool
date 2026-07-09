"""ORM model tests."""

from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session, sessionmaker

from app.db.base import Base
from app.db.init_db import init_database
from app.models import Asset, ProductionTask, Project, Script, Shot, ShotReview, Storyboard


def test_models_can_create_save_and_load_relationships(tmp_path: Path) -> None:
    database_path = tmp_path / "models.db"
    engine = create_engine(f"sqlite:///{database_path}", future=True)
    Base.metadata.create_all(bind=engine)
    test_session = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)

    with test_session() as session:
        project = Project(
            name="Steam Cleaner Campaign",
            product_name="Steam Cleaner",
            video_goal="TikTok product video",
        )
        script = Script(content="Show the product cleaning a dirty seat.", created_by="tester")
        storyboard = Storyboard()
        shot = Shot(
            shot_number=1,
            time_start=0,
            time_end=5,
            scene="Dirty car seat close-up",
            purpose="Highlight the problem",
            action="Camera pushes into the stain",
            camera="Close-up push-in",
        )
        review = ShotReview(result="approved", comment="Looks good", reviewer="reviewer_a")
        task = ProductionTask(prompt="Clean the stain with steam.", negative_prompt="blur")
        asset = Asset(
            asset_type="product_image",
            file_path="storage/assets/steam-cleaner.png",
        )

        project.scripts.append(script)
        script.storyboards.append(storyboard)
        storyboard.shots.append(shot)
        shot.reviews.append(review)
        shot.production_tasks.append(task)
        shot.assets.append(asset)

        session.add(project)
        session.commit()
        session.expire_all()

        saved_project = session.scalar(select(Project).where(Project.project_id == project.project_id))

        assert saved_project is not None
        assert len(saved_project.scripts) == 1
        assert saved_project.scripts[0].storyboards[0].shots[0].scene == "Dirty car seat close-up"

        saved_shot = saved_project.scripts[0].storyboards[0].shots[0]

        assert saved_shot.reviews[0].result == "approved"
        assert saved_shot.production_tasks[0].model == "seedance"
        assert saved_shot.assets[0].status == "required"
        assert saved_shot.production_tasks[0].assets[0].file_path.endswith("steam-cleaner.png")


def test_init_database_creates_expected_tables(tmp_path: Path, monkeypatch) -> None:
    database_path = tmp_path / "init.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{database_path}")

    from app.config import get_settings
    from app.db import session as db_session

    get_settings.cache_clear()
    db_session.settings = get_settings()
    db_session.engine.dispose()
    db_session.engine = create_engine(
        db_session.settings.database_url,
        future=True,
        connect_args={"check_same_thread": False},
    )
    db_session.SessionLocal.configure(bind=db_session.engine)

    init_database()

    assert database_path.exists()
