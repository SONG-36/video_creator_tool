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
