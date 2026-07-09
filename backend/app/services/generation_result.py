"""Generation result services."""

from __future__ import annotations

from dataclasses import dataclass

from app.models.generation_result import GenerationResult
from app.repositories.generation_result import GenerationResultRepository


class GenerationResultNotFoundError(Exception):
    """Raised when a generation result cannot be found."""


@dataclass
class GenerationResultService:
    """Read generation result details from the repository layer."""

    generation_result_repository: GenerationResultRepository

    def get_generation_result(self, result_id: str) -> GenerationResult:
        result = self.generation_result_repository.get_by_id(result_id)
        if result is None:
            raise GenerationResultNotFoundError(f"GenerationResult {result_id} not found.")
        return result
