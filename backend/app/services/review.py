"""Shot review service."""

from dataclasses import dataclass
from typing import Optional

from app.models.shot_review import ShotReview
from app.repositories.shot import ShotRepository
from app.repositories.shot_review import ShotReviewRepository


ALLOWED_REVIEW_RESULTS = {"approved", "revision_required", "rejected"}


class InvalidShotReviewTransitionError(Exception):
    """Raised when a review transition is not allowed."""


@dataclass
class ShotReviewService:
    """Apply shot review transitions using repositories only."""

    shot_repository: ShotRepository
    shot_review_repository: ShotReviewRepository

    def review_shot(
        self,
        shot_id: str,
        result: str,
        comment: str = "",
        reviewer: Optional[str] = None,
    ) -> ShotReview:
        shot = self.shot_repository.get_by_id(shot_id)
        if shot is None:
            raise InvalidShotReviewTransitionError(f"Shot {shot_id} not found.")

        if result not in ALLOWED_REVIEW_RESULTS:
            raise InvalidShotReviewTransitionError(f"Unsupported review result: {result}.")

        if shot.review_status != "waiting_review":
            raise InvalidShotReviewTransitionError(
                f"Illegal review transition: {shot.review_status} -> {result}."
            )

        updated_shot = self.shot_repository.update(shot_id, review_status=result)
        if updated_shot is None:
            raise InvalidShotReviewTransitionError(f"Shot {shot_id} not found.")

        return self.shot_review_repository.create(
            shot_id=shot_id,
            result=result,
            comment=comment,
            reviewer=reviewer or "",
        )
