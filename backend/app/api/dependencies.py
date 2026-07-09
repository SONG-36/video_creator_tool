"""API dependency providers."""

from pathlib import Path

from fastapi import Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db.session import get_db_session
from app.providers.director_provider import OpenAIDirectorProvider
from app.providers.seedance_provider import SeedanceProvider
from app.providers.skill_knowledge import FileSystemSkillKnowledgeAdapter
from app.providers.storyboard_generator import OpenAIStoryboardGeneratorProvider
from app.providers.video_provider import MockVideoProvider
from app.repositories.asset import AssetRepository
from app.repositories.generation_task import GenerationTaskRepository
from app.repositories.project import ProjectRepository
from app.repositories.production import ProductionRepository
from app.repositories.script import ScriptRepository
from app.repositories.shot import ShotRepository
from app.repositories.shot_review import ShotReviewRepository
from app.repositories.storyboard import StoryboardRepository
from app.services.asset import AssetService
from app.services.director import AIDirectorService
from app.services.generation_task import GenerationTaskService, VideoProviderRegistry
from app.services.production_type import ProductionTypeService
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


def get_asset_service(session: Session = Depends(get_db_session)) -> AssetService:
    """Build the asset service from repository dependencies."""

    settings = get_settings()
    return AssetService(
        asset_repository=AssetRepository(session),
        production_repository=ProductionRepository(session),
        storage_dir=Path(settings.asset_storage_dir),
    )


def get_storyboard_provider() -> OpenAIStoryboardGeneratorProvider:
    """Build the OpenAI storyboard generator provider."""

    return OpenAIStoryboardGeneratorProvider()


def get_video_provider_registry() -> VideoProviderRegistry:
    """Build the local provider registry for generation tasks."""

    settings = get_settings()
    return VideoProviderRegistry(
        providers={
            "mock": MockVideoProvider(),
            "seedance": SeedanceProvider(
                base_url=settings.seedance_base_url,
                api_key=settings.seedance_api_key,
            ),
        }
    )


def get_skill_knowledge_adapter() -> FileSystemSkillKnowledgeAdapter:
    """Build the filesystem-backed Seedance knowledge adapter."""

    return FileSystemSkillKnowledgeAdapter()


def get_director_provider(
    knowledge_adapter: FileSystemSkillKnowledgeAdapter = Depends(get_skill_knowledge_adapter),
) -> OpenAIDirectorProvider:
    """Build the OpenAI AI director provider."""

    return OpenAIDirectorProvider(knowledge_adapter=knowledge_adapter)


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


def get_production_type_service(session: Session = Depends(get_db_session)) -> ProductionTypeService:
    """Build the production type service from repository dependencies."""

    return ProductionTypeService(
        shot_repository=ShotRepository(session),
    )


def get_ai_director_service(
    session: Session = Depends(get_db_session),
    provider: OpenAIDirectorProvider = Depends(get_director_provider),
) -> AIDirectorService:
    """Build the AI director service from repository dependencies."""

    return AIDirectorService(
        shot_repository=ShotRepository(session),
        production_repository=ProductionRepository(session),
        asset_repository=AssetRepository(session),
        provider=provider,
    )


def get_generation_task_service(
    session: Session = Depends(get_db_session),
    provider_registry: VideoProviderRegistry = Depends(get_video_provider_registry),
) -> GenerationTaskService:
    """Build the generation task service from repository dependencies."""

    return GenerationTaskService(
        generation_task_repository=GenerationTaskRepository(session),
        production_repository=ProductionRepository(session),
        asset_repository=AssetRepository(session),
        provider_registry=provider_registry,
    )
