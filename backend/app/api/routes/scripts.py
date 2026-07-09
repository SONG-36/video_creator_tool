"""Script routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_script_service, get_storyboard_service
from app.api.schemas import (
    CreateScriptRequest,
    ScriptData,
    ScriptResponse,
    StoryboardGenerateData,
    StoryboardGenerateResponse,
)
from app.services.script import ProjectNotFoundError, ScriptNotFoundError, ScriptService
from app.services.storyboard import StoryboardGenerationFailedError, StoryboardService


router = APIRouter()


@router.post("/projects/{project_id}/scripts", response_model=ScriptResponse)
def create_script(
    project_id: str,
    payload: CreateScriptRequest,
    script_service: ScriptService = Depends(get_script_service),
) -> ScriptResponse:
    """Create a script or a new version for a project."""

    try:
        script = script_service.create_script(
            project_id=project_id,
            content=payload.content,
            created_by=payload.created_by,
        )
    except ProjectNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return ScriptResponse(data={"script": ScriptData.model_validate(script)})


@router.get("/scripts/{script_id}", response_model=ScriptResponse)
def get_script(
    script_id: str,
    script_service: ScriptService = Depends(get_script_service),
) -> ScriptResponse:
    """Get script details by identifier."""

    try:
        script = script_service.get_script(script_id)
    except ScriptNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return ScriptResponse(data={"script": ScriptData.model_validate(script)})


@router.post("/scripts/{script_id}/analyze", response_model=StoryboardGenerateResponse)
def analyze_script(
    script_id: str,
    storyboard_service: StoryboardService = Depends(get_storyboard_service),
) -> StoryboardGenerateResponse:
    """Generate a storyboard and associated shots for a script."""

    try:
        storyboard = storyboard_service.generate_storyboard(script_id)
    except ScriptNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except StoryboardGenerationFailedError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    return StoryboardGenerateResponse(
        data={
            "storyboard": StoryboardGenerateData(
                storyboard_id=storyboard.storyboard_id,
                shot_count=len(storyboard.shots),
            )
        }
    )
