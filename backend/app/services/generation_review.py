"""Generation result review service."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.models.generation_review import GenerationReview
from app.models.generation_task import GenerationTask
from app.repositories.generation_result import GenerationResultRepository
from app.repositories.generation_review import GenerationReviewRepository
from app.repositories.production import ProductionRepository
from app.services.generation_task import GenerationTaskService


ALLOWED_GENERATION_REVIEW_RESULTS = {"approved", "revision_required", "rejected"}


class InvalidGenerationReviewError(Exception):
    """Raised when a generation result review request is invalid."""


@dataclass
class GenerationReviewOutcome:
    """Return the saved review together with any follow-up generation task."""

    review: GenerationReview
    next_generation_task: Optional[GenerationTask] = None


@dataclass
class GenerationReviewService:
    """Persist result reviews and optionally create a new generation task."""

    generation_result_repository: GenerationResultRepository
    generation_review_repository: GenerationReviewRepository
    production_repository: ProductionRepository
    generation_task_service: GenerationTaskService

    def review_result(
        self,
        result_id: str,
        review_status: str,
        comment: str = "",
        reviewer: Optional[str] = None,
        regenerate: bool = False,
        prompt_override: Optional[str] = None,
    ) -> GenerationReviewOutcome:
        generation_result = self.generation_result_repository.get_by_id(result_id)
        if generation_result is None:
            raise InvalidGenerationReviewError(f"GenerationResult {result_id} not found.")

        if review_status not in ALLOWED_GENERATION_REVIEW_RESULTS:
            raise InvalidGenerationReviewError(f"Unsupported review status: {review_status}.")

        if generation_result.review_status != "reviewing":
            raise InvalidGenerationReviewError(
                f"Illegal review transition: {generation_result.review_status} -> {review_status}."
            )

        if prompt_override and review_status != "revision_required":
            raise InvalidGenerationReviewError(
                "Prompt override is only allowed when review_status is revision_required."
            )

        if regenerate and review_status == "approved":
            raise InvalidGenerationReviewError("Approved results cannot trigger regeneration.")

        updated_result = self.generation_result_repository.update(
            result_id,
            review_status=review_status,
        )
        if updated_result is None:
            raise InvalidGenerationReviewError(f"GenerationResult {result_id} not found.")

        review = self.generation_review_repository.create(
            generation_result_id=result_id,
            review_status=review_status,
            comment=comment,
            reviewer=reviewer or "",
        )

        next_generation_task: Optional[GenerationTask] = None
        if regenerate or prompt_override:
            source_task = updated_result.generation_task
            production_updates: dict[str, object] = {"status": "ready"}
            if prompt_override:
                production_updates["prompt"] = prompt_override

            updated_production_task = self.production_repository.update(
                source_task.production_task_id,
                **production_updates,
            )
            if updated_production_task is None:
                raise InvalidGenerationReviewError(
                    f"ProductionTask {source_task.production_task_id} not found."
                )

            next_generation_task = self.generation_task_service.create_generation_task(
                source_task.production_task_id,
                source_task.provider,
            )

        return GenerationReviewOutcome(
            review=review,
            next_generation_task=next_generation_task,
        )
