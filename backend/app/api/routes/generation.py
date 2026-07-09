"""Generation task routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_generation_task_service
from app.api.schemas import (
    CreateGenerationTaskRequest,
    GenerationTaskData,
    GenerationTaskResponse,
)
from app.services.generation_task import (
    GenerationTaskCreationError,
    GenerationTaskNotFoundError,
    GenerationTaskService,
    UnsupportedVideoProviderError,
)


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


@router.post("/generation/tasks", response_model=GenerationTaskResponse)
def create_generation_task(
    payload: CreateGenerationTaskRequest,
    generation_task_service: GenerationTaskService = Depends(get_generation_task_service),
) -> GenerationTaskResponse:
    """Create and queue a generation task for a ready production task."""

    try:
        task = generation_task_service.create_generation_task(
            production_task_id=payload.production_task_id,
            provider_name=payload.provider,
        )
    except UnsupportedVideoProviderError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except GenerationTaskCreationError as exc:
        message = str(exc)
        status_code = status.HTTP_404_NOT_FOUND if "not found" in message else status.HTTP_400_BAD_REQUEST
        raise HTTPException(status_code=status_code, detail=message) from exc

    return GenerationTaskResponse(data={"task": _serialize_generation_task(task)})


@router.get("/generation/tasks/{task_id}", response_model=GenerationTaskResponse)
def get_generation_task(
    task_id: str,
    generation_task_service: GenerationTaskService = Depends(get_generation_task_service),
) -> GenerationTaskResponse:
    """Fetch and refresh the latest generation task state."""

    try:
        task = generation_task_service.get_generation_task(task_id)
    except GenerationTaskNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except UnsupportedVideoProviderError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except GenerationTaskCreationError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return GenerationTaskResponse(data={"task": _serialize_generation_task(task)})
