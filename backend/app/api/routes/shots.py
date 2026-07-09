"""Shot routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import (
    get_ai_director_service,
    get_production_type_service,
    get_shot_review_service,
)
from app.api.schemas import (
    AssetRequirementData,
    ProductionPlanData,
    ProductionPlanResponse,
    ReviewShotRequest,
    SelectProductionTypeRequest,
    ShotProductionTypeData,
    ShotProductionTypeResponse,
    ShotReviewData,
    ShotReviewResponse,
)
from app.services.director import (
    AIDirectorService,
    InvalidProductionPlanRequestError,
    ProductionPlanGenerationFailedError,
    ProductionPlanNotFoundError,
)
from app.services.production_type import InvalidProductionTypeSelectionError, ProductionTypeService
from app.services.review import InvalidShotReviewTransitionError, ShotReviewService


router = APIRouter()


def _serialize_production_plan(production_task) -> ProductionPlanData:
    return ProductionPlanData(
        task_id=production_task.task_id,
        shot_id=production_task.shot_id,
        model=production_task.model,
        generation_mode=production_task.generation_mode,
        prompt=production_task.prompt,
        negative_prompt=production_task.negative_prompt,
        camera=production_task.camera,
        motion=production_task.motion,
        lighting=production_task.lighting,
        status=production_task.status,
        asset_requirement=[
            AssetRequirementData.model_validate(asset) for asset in production_task.assets
        ],
    )


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


@router.post("/shots/{shot_id}/generate-production-plan", response_model=ProductionPlanResponse)
def generate_production_plan(
    shot_id: str,
    ai_director_service: AIDirectorService = Depends(get_ai_director_service),
) -> ProductionPlanResponse:
    """Generate an AI production plan for an AI-generated shot."""

    try:
        production_task = ai_director_service.generate_production_plan(shot_id)
    except InvalidProductionPlanRequestError as exc:
        message = str(exc)
        status_code = status.HTTP_404_NOT_FOUND if "not found" in message else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=message) from exc
    except ProductionPlanGenerationFailedError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return ProductionPlanResponse(data={"production_task": _serialize_production_plan(production_task)})


@router.get("/shots/{shot_id}/production-plan", response_model=ProductionPlanResponse)
def get_production_plan(
    shot_id: str,
    ai_director_service: AIDirectorService = Depends(get_ai_director_service),
) -> ProductionPlanResponse:
    """Get the latest AI production plan for a shot."""

    try:
        production_task = ai_director_service.get_production_plan(shot_id)
    except ProductionPlanNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return ProductionPlanResponse(data={"production_task": _serialize_production_plan(production_task)})
