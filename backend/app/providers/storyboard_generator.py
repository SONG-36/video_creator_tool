"""Providers for storyboard generation."""

from __future__ import annotations

import json
from typing import Optional, Protocol

from pydantic import BaseModel, ConfigDict, Field

from app.config import get_settings
from app.models.script import Script


class StoryboardGenerationError(Exception):
    """Raised when storyboard generation fails."""


class TimeRangeSchema(BaseModel):
    """Structured time range for a generated shot."""

    start: int = Field(ge=0)
    end: int = Field(gt=0)


class GeneratedShotSchema(BaseModel):
    """Structured shot payload returned by the model."""

    shot_number: int = Field(ge=1)
    time_range: TimeRangeSchema
    scene: str
    purpose: str
    action: str
    camera: str
    production_type: str = "pending"
    review_status: str = "waiting_review"


class StoryboardGenerationResult(BaseModel):
    """Structured storyboard payload returned by the provider."""

    model_config = ConfigDict(extra="forbid")

    shots: list[GeneratedShotSchema]


class StoryboardGenerationProvider(Protocol):
    """Provider contract for generating storyboard data."""

    def generate_storyboard(self, script: Script) -> StoryboardGenerationResult:
        """Generate storyboard data from a script."""


class OpenAIStoryboardGeneratorProvider:
    """OpenAI-backed storyboard generation provider."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        base_url: Optional[str] = None,
    ) -> None:
        settings = get_settings()
        self.api_key = api_key or settings.openai_api_key
        self.model = model or settings.openai_model
        self.base_url = base_url or settings.openai_base_url

    def _build_client(self):
        if not self.api_key:
            raise StoryboardGenerationError("OPENAI_API_KEY is not configured.")

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise StoryboardGenerationError("openai package is not installed.") from exc

        client_kwargs = {"api_key": self.api_key}
        if self.base_url:
            client_kwargs["base_url"] = self.base_url

        return OpenAI(**client_kwargs)

    def generate_storyboard(self, script: Script) -> StoryboardGenerationResult:
        client = self._build_client()
        response = client.responses.create(
            model=self.model,
            instructions=self._system_instructions(),
            input=self._build_prompt(script),
            text={
                "format": {
                    "type": "json_schema",
                    "name": "storyboard_generation",
                    "schema": StoryboardGenerationResult.model_json_schema(),
                    "strict": True,
                }
            },
        )

        output_text = getattr(response, "output_text", None)
        if not output_text:
            raise StoryboardGenerationError("OpenAI response did not include structured output text.")

        try:
            payload = json.loads(output_text)
            return StoryboardGenerationResult.model_validate(payload)
        except Exception as exc:
            raise StoryboardGenerationError("Failed to parse OpenAI storyboard response.") from exc

    @staticmethod
    def _system_instructions() -> str:
        return (
            "You are a storyboard generator for short product videos. "
            "Return only structured shot data that matches the provided JSON schema. "
            "Generate at least two shots when the script supports multiple beats. "
            "Keep production_type as pending and review_status as waiting_review."
        )

    @staticmethod
    def _build_prompt(script: Script) -> str:
        return (
            "Convert the following script into a storyboard shot list. "
            "Each shot must include shot_number, time_range, scene, purpose, action, camera, "
            "production_type, and review_status.\n\n"
            f"Script ID: {script.script_id}\n"
            f"Project ID: {script.project_id}\n"
            f"Content:\n{script.content}"
        )
