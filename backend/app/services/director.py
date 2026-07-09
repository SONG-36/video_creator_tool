"""AI Director service."""

from dataclasses import dataclass

from app.models.production_task import ProductionTask
from app.providers.director_provider import DirectorGenerationError, DirectorProvider
from app.repositories.asset import AssetRepository
from app.repositories.production import ProductionRepository
from app.repositories.shot import ShotRepository


class InvalidProductionPlanRequestError(Exception):
    """Raised when a shot is not eligible for AI production planning."""


class ProductionPlanGenerationFailedError(Exception):
    """Raised when the AI director provider cannot generate a plan."""


class ProductionPlanNotFoundError(Exception):
    """Raised when a production plan cannot be found."""


@dataclass
class AIDirectorService:
    """Generate and read AI production plans using repositories only."""

    shot_repository: ShotRepository
    production_repository: ProductionRepository
    asset_repository: AssetRepository
    provider: DirectorProvider

    def generate_production_plan(self, shot_id: str) -> ProductionTask:
        shot = self.shot_repository.get_by_id(shot_id)
        if shot is None:
            raise InvalidProductionPlanRequestError(f"Shot {shot_id} not found.")

        if shot.production_type != "ai_generate":
            raise InvalidProductionPlanRequestError(
                "Only shots with production_type ai_generate can generate an AI production plan."
            )

        try:
            plan = self.provider.generate_plan(shot)
        except DirectorGenerationError as exc:
            raise ProductionPlanGenerationFailedError(str(exc)) from exc

        status = "waiting_asset" if plan.asset_requirement else "ready"
        production_task = self.production_repository.create(
            shot_id=shot_id,
            model="seedance",
            generation_mode=plan.generation_mode,
            prompt=plan.prompt,
            negative_prompt=plan.negative_prompt,
            camera=plan.camera,
            motion=plan.motion,
            lighting=plan.lighting,
            status=status,
        )

        created_assets = []
        for requirement in plan.asset_requirement:
            created_assets.append(
                self.asset_repository.create(
                    shot_id=shot_id,
                    production_task_id=production_task.task_id,
                    asset_type=requirement.asset_type,
                    role=requirement.role,
                    reference_tag=requirement.reference_tag,
                    requirement_note=requirement.requirement_note,
                    file_path="",
                    status="required",
                )
            )

        production_task.assets = created_assets
        return production_task

    def get_production_plan(self, shot_id: str) -> ProductionTask:
        shot = self.shot_repository.get_by_id(shot_id)
        if shot is None:
            raise ProductionPlanNotFoundError(f"Shot {shot_id} not found.")

        production_task = self.production_repository.get_latest_by_shot_id(shot_id)
        if production_task is None:
            raise ProductionPlanNotFoundError(f"Production plan for shot {shot_id} not found.")

        return production_task
