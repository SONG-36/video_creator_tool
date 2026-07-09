"""Generation task service."""

from __future__ import annotations

from dataclasses import dataclass

from app.models.generation_task import GenerationTask
from app.providers.video_provider import VideoProvider, VideoProviderError
from app.repositories.asset import AssetRepository
from app.repositories.generation_task import GenerationTaskRepository
from app.repositories.production import ProductionRepository


ALLOWED_GENERATION_STATUSES = {"pending", "queued", "running", "completed", "failed"}


class GenerationTaskCreationError(Exception):
    """Raised when a generation task cannot be created."""


class GenerationTaskNotFoundError(Exception):
    """Raised when a generation task cannot be found."""


class UnsupportedVideoProviderError(Exception):
    """Raised when a requested provider is not available."""


@dataclass
class VideoProviderRegistry:
    """Resolve provider names to provider implementations."""

    providers: dict[str, VideoProvider]

    def get(self, provider_name: str) -> VideoProvider:
        provider = self.providers.get(provider_name)
        if provider is None:
            raise UnsupportedVideoProviderError(f"Unsupported provider: {provider_name}.")
        return provider


@dataclass
class GenerationTaskService:
    """Manage asynchronous video generation tasks through repositories and providers."""

    generation_task_repository: GenerationTaskRepository
    production_repository: ProductionRepository
    asset_repository: AssetRepository
    provider_registry: VideoProviderRegistry

    def create_generation_task(self, production_task_id: str, provider_name: str) -> GenerationTask:
        production_task = self.production_repository.get_by_id(production_task_id)
        if production_task is None:
            raise GenerationTaskCreationError(f"ProductionTask {production_task_id} not found.")

        if production_task.status != "ready":
            raise GenerationTaskCreationError(
                "Only ProductionTask records with status ready can create a GenerationTask."
            )

        provider = self.provider_registry.get(provider_name)
        request_payload = self._build_request_payload(production_task_id)
        generation_task = self.generation_task_repository.create(
            production_task_id=production_task_id,
            provider=provider_name,
            status="pending",
            request_payload=request_payload,
            result_payload=None,
            error_message="",
        )

        try:
            provider_response = provider.create_task(generation_task)
        except VideoProviderError as exc:
            failed_task = self.generation_task_repository.update(
                generation_task.task_id,
                status="failed",
                error_message=str(exc),
            )
            self.production_repository.update(production_task_id, status="failed")
            if failed_task is None:
                raise GenerationTaskCreationError(str(exc)) from exc
            return failed_task

        queued_task = self.generation_task_repository.update(
            generation_task.task_id,
            status="queued",
            request_payload={**request_payload, "provider_request": provider_response},
        )
        self.production_repository.update(production_task_id, status="generating")

        if queued_task is None:
            raise GenerationTaskCreationError("GenerationTask could not be queued.")

        return queued_task

    def get_generation_task(self, task_id: str) -> GenerationTask:
        generation_task = self.generation_task_repository.get_by_id(task_id)
        if generation_task is None:
            raise GenerationTaskNotFoundError(f"GenerationTask {task_id} not found.")

        if generation_task.status in {"completed", "failed"}:
            return generation_task

        provider = self.provider_registry.get(generation_task.provider)
        next_status = provider.get_status(generation_task)
        if next_status not in ALLOWED_GENERATION_STATUSES:
            raise GenerationTaskCreationError(f"Unsupported generation task status: {next_status}.")

        updates = {"status": next_status}
        if next_status == "completed":
            updates["result_payload"] = provider.get_result(generation_task)
            updates["error_message"] = ""
        elif next_status == "failed":
            updates["error_message"] = "Video provider task failed."

        refreshed_task = self.generation_task_repository.update(task_id, **updates)
        if refreshed_task is None:
            raise GenerationTaskNotFoundError(f"GenerationTask {task_id} not found.")

        self._sync_production_status(refreshed_task)
        return refreshed_task

    def _build_request_payload(self, production_task_id: str) -> dict:
        production_task = self.production_repository.get_by_id(production_task_id)
        if production_task is None:
            raise GenerationTaskCreationError(f"ProductionTask {production_task_id} not found.")

        assets = self.asset_repository.list_by_production_task_id(production_task_id)
        return {
            "production_task_id": production_task.task_id,
            "shot_id": production_task.shot_id,
            "model": production_task.model,
            "generation_mode": production_task.generation_mode,
            "prompt": production_task.prompt,
            "negative_prompt": production_task.negative_prompt,
            "camera": production_task.camera,
            "motion": production_task.motion,
            "lighting": production_task.lighting,
            "assets": [
                {
                    "asset_id": asset.asset_id,
                    "asset_type": asset.asset_type,
                    "role": asset.role,
                    "reference_tag": asset.reference_tag,
                    "file_path": asset.file_path,
                    "status": asset.status,
                }
                for asset in assets
            ],
        }

    def _sync_production_status(self, generation_task: GenerationTask) -> None:
        if generation_task.status in {"queued", "running"}:
            self.production_repository.update(generation_task.production_task_id, status="generating")
        elif generation_task.status == "completed":
            self.production_repository.update(generation_task.production_task_id, status="completed")
        elif generation_task.status == "failed":
            self.production_repository.update(generation_task.production_task_id, status="failed")
