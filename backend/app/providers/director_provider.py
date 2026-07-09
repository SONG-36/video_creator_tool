"""Providers for AI director production plan generation."""

from __future__ import annotations

import json
from typing import Optional, Protocol

from pydantic import BaseModel, ConfigDict, Field

from app.config import get_settings
from app.models.shot import Shot
from app.providers.skill_knowledge import (
    FileSystemSkillKnowledgeAdapter,
    SkillKnowledgeAdapter,
    SkillKnowledgeError,
)


class DirectorGenerationError(Exception):
    """Raised when AI director generation fails."""


class AssetRequirementSchema(BaseModel):
    """Structured asset requirement returned by the AI director."""

    model_config = ConfigDict(extra="forbid")

    asset_type: str = Field(
        description=(
            "One of: product_image, product_detail_image, first_frame, "
            "reference_image, reference_video, audio."
        )
    )
    role: str
    reference_tag: str
    requirement_note: str


class DirectorPlanResult(BaseModel):
    """Structured production plan returned by the AI director."""

    model_config = ConfigDict(extra="forbid")

    generation_mode: str
    prompt: str
    negative_prompt: str
    camera: str
    motion: str
    lighting: str
    asset_requirement: list[AssetRequirementSchema] = Field(default_factory=list)


class DirectorProvider(Protocol):
    """Provider contract for AI director generation."""

    def generate_plan(self, shot: Shot) -> DirectorPlanResult:
        """Generate a structured production plan from a shot."""


class OpenAIDirectorProvider:
    """OpenAI-backed AI director provider."""

    def __init__(
        self,
        knowledge_adapter: Optional[SkillKnowledgeAdapter] = None,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        settings = get_settings()
        self.knowledge_adapter = knowledge_adapter or FileSystemSkillKnowledgeAdapter()
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        self.base_url = base_url or settings.openai_base_url

    def _build_client(self):
        if not self.api_key:
            raise DirectorGenerationError("OPENAI_API_KEY is not configured.")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise DirectorGenerationError("openai package is not installed.") from exc

        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        return OpenAI(**client_kwargs)

    def generate_plan(self, shot: Shot) -> DirectorPlanResult:
        try:
            knowledge = self.knowledge_adapter.load_seedance_knowledge()
        except SkillKnowledgeError as exc:
            raise DirectorGenerationError(str(exc)) from exc

        client = self._build_client()
        response = client.responses.create(
            model=self.model,
            instructions=self._system_instructions(knowledge),
            input=self._build_prompt(shot),
            text={
                "format": {
                    "type": "json_schema",
                    "name": "ai_director_plan",
                    "schema": DirectorPlanResult.model_json_schema(),
                    "strict": True,
                }
            },
        )

        output_text = getattr(response, "output_text", None)
        if not output_text:
            raise DirectorGenerationError("OpenAI response did not include structured output text.")

        try:
            payload = json.loads(output_text)
            return DirectorPlanResult.model_validate(payload)
        except Exception as exc:
            raise DirectorGenerationError("Failed to parse AI director response.") from exc

    @staticmethod
    def _system_instructions(knowledge) -> str:
        return (
            "You are the AI Director for a short-video production workflow. "
            "Generate a structured Seedance production plan that matches the JSON schema exactly. "
            "Preserve reference tags exactly as written. "
            "Use only the supported asset types: product_image, product_detail_image, "
            "first_frame, reference_image, reference_video, audio. "
            "When assets are needed, every asset requirement must include asset_type, role, "
            "reference_tag, and requirement_note. "
            "Return concise production-ready text.\n\n"
            "Reference workflow knowledge:\n"
            f"{knowledge.reference_workflow}\n\n"
            "Prompt guidance:\n"
            f"{knowledge.prompt_guidance}\n\n"
            "Camera guidance:\n"
            f"{knowledge.camera_guidance}\n\n"
            "Motion guidance:\n"
            f"{knowledge.motion_guidance}"
        )

    @staticmethod
    def _build_prompt(shot: Shot) -> str:
        storyboard = getattr(shot, "storyboard", None)
        script = getattr(storyboard, "script", None) if storyboard is not None else None
        project = getattr(script, "project", None) if script is not None else None

        project_name = project.name if project is not None else ""
        product_name = project.product_name if project is not None else ""
        video_goal = project.video_goal if project is not None else ""
        script_content = script.content if script is not None else ""

        return (
            "Build an AI production plan for the following shot.\n\n"
            f"Project: {project_name}\n"
            f"Product: {product_name}\n"
            f"Video Goal: {video_goal}\n"
            f"Script Content: {script_content}\n"
            f"Shot ID: {shot.shot_id}\n"
            f"Shot Number: {shot.shot_number}\n"
            f"Scene: {shot.scene}\n"
            f"Purpose: {shot.purpose}\n"
            f"Action: {shot.action}\n"
            f"Existing Camera: {shot.camera}\n"
            f"Production Type: {shot.production_type}\n"
            f"Review Status: {shot.review_status}\n\n"
            "Choose the best generation_mode for Seedance and generate a complete plan. "
            "If references are required, use exact tags like @Image1 or @Video1 and explain "
            "their role in requirement_note."
        )
