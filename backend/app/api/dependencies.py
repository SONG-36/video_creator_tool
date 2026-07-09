"""API dependency providers."""

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.session import get_db_session
from app.providers.storyboard_generator import OpenAIStoryboardGeneratorProvider
from app.repositories.project import ProjectRepository
from app.repositories.script import ScriptRepository
from app.repositories.shot import ShotRepository
from app.repositories.shot_review import ShotReviewRepository
from app.repositories.storyboard import StoryboardRepository
from app.services.review import ShotReviewService
from app.services.script import ScriptService
from app.services.storyboard import StoryboardService


def get_script_service(session: Session = Depends(get_db_session)) -> ScriptService:
    """Build the script service from repository dependencies."""

    project_repository = ProjectRepository(session)
    script_repository = ScriptRepository(session)
    return ScriptService(
        project_repository=project_repository,
        script_repository=script_repository,
    )


def get_storyboard_provider() -> OpenAIStoryboardGeneratorProvider:
    """Build the OpenAI storyboard generator provider."""

    return OpenAIStoryboardGeneratorProvider()


def get_storyboard_service(
    session: Session = Depends(get_db_session),
    provider: OpenAIStoryboardGeneratorProvider = Depends(get_storyboard_provider),
) -> StoryboardService:
    """Build the storyboard service from repository dependencies."""

    return StoryboardService(
        script_repository=ScriptRepository(session),
        storyboard_repository=StoryboardRepository(session),
        shot_repository=ShotRepository(session),
        provider=provider,
    )


def get_shot_review_service(session: Session = Depends(get_db_session)) -> ShotReviewService:
    """Build the shot review service from repository dependencies."""

    return ShotReviewService(
        shot_repository=ShotRepository(session),
        shot_review_repository=ShotReviewRepository(session),
    )
