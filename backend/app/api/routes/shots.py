"""Shot routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_production_type_service, get_shot_review_service
from app.api.schemas import (
    ReviewShotRequest,
    SelectProductionTypeRequest,
    ShotProductionTypeData,
    ShotProductionTypeResponse,
    ShotReviewData,
    ShotReviewResponse,
)
from app.services.production_type import InvalidProductionTypeSelectionError, ProductionTypeService
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


@router.post("/shots/{shot_id}/production-type", response_model=ShotProductionTypeResponse)
def select_production_type(
    shot_id: str,
    payload: SelectProductionTypeRequest,
    production_type_service: ProductionTypeService = Depends(get_production_type_service),
) -> ShotProductionTypeResponse:
    """Select the production type for an approved shot."""

    try:
        shot = production_type_service.select_production_type(
            shot_id=shot_id,
            production_type=payload.production_type,
        )
    except InvalidProductionTypeSelectionError as exc:
        message = str(exc)
        status_code = status.HTTP_404_NOT_FOUND if "not found" in message else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=message) from exc

    return ShotProductionTypeResponse(
        data={
            "shot": ShotProductionTypeData(
                shot_id=shot.shot_id,
                production_type=shot.production_type,
                review_status=shot.review_status,
            )
        }
    )
