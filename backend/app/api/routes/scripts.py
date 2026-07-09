"""Script routes."""

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.dependencies import get_script_service
from app.api.schemas import CreateScriptRequest, ScriptData, ScriptResponse
from app.services.script import ProjectNotFoundError, ScriptNotFoundError, ScriptService


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
