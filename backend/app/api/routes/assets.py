"""Asset routes."""

from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status

from app.api.dependencies import get_asset_service
from app.api.schemas import (
    AssetData,
    AssetListData,
    AssetListResponse,
    AssetResponse,
    UpdateAssetStatusRequest,
)
from app.services.asset import (
    AssetNotFoundError,
    AssetService,
    AssetStatusError,
    AssetUploadError,
    ProductionTaskAssetError,
)


router = APIRouter()


def _serialize_asset(asset) -> AssetData:
    file_name = Path(asset.file_path).name if asset.file_path else None
    file_size = None
    if asset.file_path:
        path = Path(asset.file_path)
        if path.exists():
            file_size = path.stat().st_size

    return AssetData(
        asset_id=asset.asset_id,
        shot_id=asset.shot_id,
        production_task_id=asset.production_task_id,
        asset_type=asset.asset_type,
        role=asset.role,
        reference_tag=asset.reference_tag,
        requirement_note=asset.requirement_note,
        file_path=asset.file_path,
        file_name=file_name,
        file_size=file_size,
        status=asset.status,
    )


@router.post("/assets/upload", response_model=AssetResponse)
async def upload_asset(
    production_task_id: str = Form(...),
    role: str = Form(...),
    reference_tag: str = Form(...),
    requirement_note: str = Form(""),
    file: UploadFile = File(...),
    asset_service: AssetService = Depends(get_asset_service),
) -> AssetResponse:
    """Upload a managed asset for a production task."""

    try:
        asset = asset_service.upload_asset(
            production_task_id=production_task_id,
            role=role,
            reference_tag=reference_tag,
            requirement_note=requirement_note,
            filename=file.filename or "upload.bin",
            content=await file.read(),
            content_type=file.content_type or "",
        )
    except ProductionTaskAssetError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AssetUploadError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return AssetResponse(data={"asset": _serialize_asset(asset)})


@router.get("/production-tasks/{task_id}/assets", response_model=AssetListResponse)
def list_assets(
    task_id: str,
    asset_service: AssetService = Depends(get_asset_service),
) -> AssetListResponse:
    """List all assets associated with a production task."""

    try:
        assets = asset_service.list_assets(task_id)
    except ProductionTaskAssetError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc

    return AssetListResponse(
        data={
            "assets": AssetListData(
                production_task_id=task_id,
                assets=[_serialize_asset(asset) for asset in assets],
            )
        }
    )


@router.patch("/assets/{asset_id}/status", response_model=AssetResponse)
def update_asset_status(
    asset_id: str,
    payload: UpdateAssetStatusRequest,
    asset_service: AssetService = Depends(get_asset_service),
) -> AssetResponse:
    """Update the status of an uploaded asset."""

    try:
        asset = asset_service.update_asset_status(asset_id, payload.status)
    except AssetNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except AssetStatusError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc

    return AssetResponse(data={"asset": _serialize_asset(asset)})
