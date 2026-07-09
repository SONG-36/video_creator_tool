"""Production type selection service."""

from dataclasses import dataclass

from app.models.shot import Shot
from app.repositories.shot import ShotRepository


ALLOWED_PRODUCTION_TYPES = {"real_shoot", "ai_generate"}


class InvalidProductionTypeSelectionError(Exception):
    """Raised when a shot cannot select the requested production type."""


@dataclass
class ProductionTypeService:
    """Select a shot production type using repository access only."""

    shot_repository: ShotRepository

    def select_production_type(self, shot_id: str, production_type: str) -> Shot:
        shot = self.shot_repository.get_by_id(shot_id)
        if shot is None:
            raise InvalidProductionTypeSelectionError(f"Shot {shot_id} not found.")

        if production_type not in ALLOWED_PRODUCTION_TYPES:
            raise InvalidProductionTypeSelectionError(
                f"Unsupported production_type: {production_type}."
            )

        if shot.review_status != "approved":
            raise InvalidProductionTypeSelectionError(
                "Only approved shots can select a production type."
            )

        updated_shot = self.shot_repository.update(shot_id, production_type=production_type)
        if updated_shot is None:
            raise InvalidProductionTypeSelectionError(f"Shot {shot_id} not found.")

        return updated_shot
