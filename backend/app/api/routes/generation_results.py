"""Generation result routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_generation_result_service, get_generation_review_service
from app.api.schemas import (
    GenerationResultData,
    GenerationResultResponse,
    GenerationResultReviewData,
    GenerationResultReviewResponse,
    GenerationTaskData,
    ReviewGenerationResultRequest,
)
from app.services.generation_result import GenerationResultNotFoundError, GenerationResultService
from app.services.generation_review import GenerationReviewService, InvalidGenerationReviewError


router = APIRouter()


def _serialize_generation_task(task) -> GenerationTaskData:
    return GenerationTaskData(
        task_id=task.task_id,
        production_task_id=task.production_task_id,
        provider=task.provider,
        status=task.status,
        request_payload=task.request_payload,
        result_payload=task.result_payload,
        error_message=task.error_message,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


def _serialize_generation_result(result) -> GenerationResultData:
    payload = result.generation_task.request_payload or {}
    return GenerationResultData(
        result_id=result.id,
        generation_task_id=result.generation_task_id,
        production_task_id=result.generation_task.production_task_id,
        shot_id=payload.get("shot_id", ""),
        provider=result.generation_task.provider,
        prompt=payload.get("prompt", ""),
        negative_prompt=payload.get("negative_prompt", ""),
        camera=payload.get("camera", ""),
        motion=payload.get("motion", ""),
        lighting=payload.get("lighting", ""),
        video_url=result.video_url,
        video_path=result.video_path,
        thumbnail_url=result.thumbnail_url,
        version=result.version,
        generation_cost=result.generation_cost,
        status=result.status,
        review_status=result.review_status,
        created_at=result.created_at,
        updated_at=result.updated_at,
    )


@router.get("/generation-results/{result_id}", response_model=GenerationResultResponse)
def get_generation_result(
    result_id: str,
    generation_result_service: GenerationResultService = Depends(get_generation_result_service),
) -> GenerationResultResponse:
    """Fetch one generated video result."""

    try:
        result = generation_result_service.get_generation_result(result_id)
    except GenerationResultNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return GenerationResultResponse(data={"result": _serialize_generation_result(result)})


@router.post(
    "/generation-results/{result_id}/review",
    response_model=GenerationResultReviewResponse,
)
def review_generation_result(
    result_id: str,
    payload: ReviewGenerationResultRequest,
    generation_review_service: GenerationReviewService = Depends(get_generation_review_service),
) -> GenerationResultReviewResponse:
    """Save a review for one generated video result and optionally regenerate."""

    try:
        outcome = generation_review_service.review_result(
            result_id=result_id,
            review_status=payload.review_status,
            comment=payload.comment,
            reviewer=payload.reviewer,
            regenerate=payload.regenerate,
            prompt_override=payload.prompt_override,
        )
    except InvalidGenerationReviewError as exc:
        message = str(exc)
        status_code = status.HTTP_404_NOT_FOUND if "not found" in message else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=message) from exc

    return GenerationResultReviewResponse(
        data={
            "review": GenerationResultReviewData(
                review=outcome.review,
                next_generation_task=(
                    _serialize_generation_task(outcome.next_generation_task)
                    if outcome.next_generation_task is not None
                    else None
                ),
            )
        }
    )
