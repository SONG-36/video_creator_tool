"""Video generation provider abstractions and mock implementation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.models.generation_task import GenerationTask


class VideoProviderError(Exception):
    """Raised when a video provider operation fails."""


class VideoProvider(ABC):
    """Provider contract for asynchronous video generation."""

    @abstractmethod
    def create_task(self, generation_task: GenerationTask) -> dict:
        """Submit a generation task to the provider."""

    @abstractmethod
    def get_status(self, generation_task: GenerationTask) -> str:
        """Fetch the latest provider status."""

    @abstractmethod
    def get_result(self, generation_task: GenerationTask) -> dict:
        """Return the latest provider result payload."""


@dataclass
class MockVideoProvider(VideoProvider):
    """Local mock provider used for deterministic task state progression."""

    def create_task(self, generation_task: GenerationTask) -> dict:
        return {
            "provider_task_id": generation_task.task_id,
            "provider": "mock",
            "accepted": True,
        }

    def get_status(self, generation_task: GenerationTask) -> str:
        if generation_task.status in {"pending", "queued"}:
            return "running"
        if generation_task.status == "running":
            return "completed"
        return generation_task.status

    def get_result(self, generation_task: GenerationTask) -> dict:
        return {
            "video_path": f"storage/generated/{generation_task.task_id}.mp4",
            "provider": generation_task.provider,
            "production_task_id": generation_task.production_task_id,
            "status": "completed",
        }
