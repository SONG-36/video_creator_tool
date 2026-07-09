"""Shot routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_shot_review_service
from app.api.schemas import ReviewShotRequest, ShotReviewData, ShotReviewResponse
from app.services.review import InvalidShotReviewTransitionError, ShotReviewService


router = APIRouter()


@router.post("/shots/{shot_id}/review", response_model=ShotReviewResponse)
def review_shot(
    shot_id: str,
    payload: ReviewShotRequest,
    review_service: ShotReviewService = Depends(get_shot_review_service),
) -> ShotReviewResponse:
    """Review a storyboard shot and persist the audit record."""

    try:
        review = review_service.review_shot(
            shot_id=shot_id,
            result=payload.result,
            comment=payload.comment,
            reviewer=payload.reviewer,
        )
    except InvalidShotReviewTransitionError as exc:
        message = str(exc)
        status_code = status.HTTP_404_NOT_FOUND if "not found" in message else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=message) from exc

    return ShotReviewResponse(data={"review": ShotReviewData.model_validate(review)})
