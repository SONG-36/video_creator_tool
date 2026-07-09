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
