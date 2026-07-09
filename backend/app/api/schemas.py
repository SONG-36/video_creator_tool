"""Pydantic schemas for API requests and responses."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class ApiResponse(BaseModel):
    """Standard API response envelope."""

    code: int = 0
    message: str = "success"
    data: dict


class CreateScriptRequest(BaseModel):
    """Payload for creating a project script."""

    content: str
    created_by: Optional[str] = None


class ScriptData(BaseModel):
    """Serialized script payload."""

    model_config = ConfigDict(from_attributes=True)

    script_id: str
    project_id: str
    content: str
    version: int
    status: str
    created_by: Optional[str]
    created_at: datetime


class ScriptResponse(ApiResponse):
    """Response envelope carrying a script payload."""

    data: dict[str, ScriptData]


class StoryboardGenerateData(BaseModel):
    """Payload returned after storyboard generation."""

    storyboard_id: str
    shot_count: int


class StoryboardGenerateResponse(ApiResponse):
    """Response envelope carrying generated storyboard metadata."""

    data: dict[str, StoryboardGenerateData]


class ReviewShotRequest(BaseModel):
    """Payload for reviewing a shot."""

    result: str
    comment: str = ""
    reviewer: Optional[str] = None


class ShotReviewData(BaseModel):
    """Serialized shot review payload."""

    model_config = ConfigDict(from_attributes=True)

    review_id: str
    shot_id: str
    review_type: str
    result: str
    comment: str
    reviewer: str
    created_at: datetime


class ShotReviewResponse(ApiResponse):
    """Response envelope carrying a shot review payload."""

    data: dict[str, ShotReviewData]


class SelectProductionTypeRequest(BaseModel):
    """Payload for selecting a shot production type."""

    production_type: str


class ShotProductionTypeData(BaseModel):
    """Serialized shot production type payload."""

    shot_id: str
    production_type: str
    review_status: str


class ShotProductionTypeResponse(ApiResponse):
    """Response envelope carrying a shot production selection."""

    data: dict[str, ShotProductionTypeData]


class AssetRequirementData(BaseModel):
    """Serialized asset requirement payload."""

    model_config = ConfigDict(from_attributes=True)

    asset_id: str
    asset_type: str
    role: str
    reference_tag: str
    requirement_note: str
    status: str


class ProductionPlanData(BaseModel):
    """Serialized AI production plan payload."""

    task_id: str
    shot_id: str
    model: str
    generation_mode: str
    prompt: str
    negative_prompt: str
    camera: str
    motion: str
    lighting: str
    status: str
    asset_requirement: list[AssetRequirementData]


class ProductionPlanResponse(ApiResponse):
    """Response envelope carrying an AI production plan."""

    data: dict[str, ProductionPlanData]


class UpdateAssetStatusRequest(BaseModel):
    """Payload for updating an asset status."""

    status: str


class AssetData(BaseModel):
    """Serialized asset payload."""

    asset_id: str
    shot_id: str
    production_task_id: Optional[str]
    asset_type: str
    role: str
    reference_tag: str
    requirement_note: str
    file_path: str
    file_name: Optional[str]
    file_size: Optional[int]
    status: str


class AssetResponse(ApiResponse):
    """Response envelope carrying one asset payload."""

    data: dict[str, AssetData]


class AssetListData(BaseModel):
    """Serialized list payload for production task assets."""

    production_task_id: str
    assets: list[AssetData]


class AssetListResponse(ApiResponse):
    """Response envelope carrying a production task asset list."""

    data: dict[str, AssetListData]


class CreateGenerationTaskRequest(BaseModel):
    """Payload for creating a generation task."""

    production_task_id: str
    provider: str = "mock"


class GenerationTaskData(BaseModel):
    """Serialized generation task payload."""

    task_id: str
    production_task_id: str
    provider: str
    status: str
    request_payload: dict
    result_payload: Optional[dict]
    error_message: str
    created_at: datetime
    updated_at: datetime


class GenerationTaskResponse(ApiResponse):
    """Response envelope carrying one generation task."""

    data: dict[str, GenerationTaskData]
