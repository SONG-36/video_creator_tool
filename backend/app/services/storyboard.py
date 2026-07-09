"""Storyboard service."""

from dataclasses import dataclass

from app.models.storyboard import Storyboard
from app.providers.storyboard_generator import (
    StoryboardGenerationError,
    StoryboardGenerationProvider,
)
from app.repositories.script import ScriptRepository
from app.repositories.shot import ShotRepository
from app.repositories.storyboard import StoryboardRepository
from app.services.script import ScriptNotFoundError


class StoryboardGenerationFailedError(Exception):
    """Raised when storyboard generation cannot be completed."""


@dataclass
class StoryboardService:
    """Create storyboards and shots from scripts using repositories only."""

    script_repository: ScriptRepository
    storyboard_repository: StoryboardRepository
    shot_repository: ShotRepository
    provider: StoryboardGenerationProvider

    def generate_storyboard(self, script_id: str) -> Storyboard:
        script = self.script_repository.get_by_id(script_id)
        if script is None:
            raise ScriptNotFoundError(f"Script {script_id} not found.")

        try:
            generated = self.provider.generate_storyboard(script)
        except StoryboardGenerationError as exc:
            raise StoryboardGenerationFailedError(str(exc)) from exc

        existing_storyboards = self.storyboard_repository.list_by_script_id(script_id)
        next_version = max((storyboard.version for storyboard in existing_storyboards), default=0) + 1

        storyboard = self.storyboard_repository.create(
            script_id=script_id,
            version=next_version,
            status="draft",
        )
        shots_payload = [
            {
                "storyboard_id": storyboard.storyboard_id,
                "shot_number": shot.shot_number,
                "time_start": shot.time_range.start,
                "time_end": shot.time_range.end,
                "scene": shot.scene,
                "purpose": shot.purpose,
                "action": shot.action,
                "camera": shot.camera,
                "production_type": shot.production_type,
                "review_status": shot.review_status,
            }
            for shot in generated.shots
        ]
        created_shots = self.shot_repository.create_many(shots_payload)
        storyboard.shots = created_shots
        return storyboard
