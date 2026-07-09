"""Seedance video provider implementation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional

import httpx

from app.models.generation_task import GenerationTask
from app.providers.video_provider import VideoProvider, VideoProviderError


STATUS_MAPPING = {
    "pending": "pending",
    "created": "pending",
    "queued": "queued",
    "submitted": "queued",
    "running": "running",
    "processing": "running",
    "generating": "running",
    "completed": "completed",
    "succeeded": "completed",
    "success": "completed",
    "finished": "completed",
    "failed": "failed",
    "error": "failed",
    "cancelled": "failed",
}


@dataclass
class SeedanceProvider(VideoProvider):
    """Translate GenerationTask payloads into Seedance API requests."""

    base_url: str
    api_key: str
    timeout: float = 30.0
    http_client: Optional[httpx.Client] = field(default=None, repr=False)

    def create_task(self, generation_task: GenerationTask) -> dict:
        payload = self._build_seedance_payload(generation_task)
        response = self._request("POST", "/tasks", json=payload)
        provider_task_id = self._extract_provider_task_id(response)
        return {
            "provider": "seedance",
            "provider_task_id": provider_task_id,
            "accepted": True,
            "seedance_request": payload,
        }

    def get_status(self, generation_task: GenerationTask) -> str:
        provider_task_id = self._get_provider_task_id(generation_task)
        response = self._request("GET", f"/tasks/{provider_task_id}")
        remote_status = self._extract_status(response)
        try:
            return STATUS_MAPPING[remote_status.lower()]
        except KeyError as exc:
            raise VideoProviderError(f"Unsupported Seedance status: {remote_status}.") from exc

    def get_result(self, generation_task: GenerationTask) -> dict:
        provider_task_id = self._get_provider_task_id(generation_task)
        response = self._request("GET", f"/tasks/{provider_task_id}/result")
        data = self._extract_data(response)
        result = data.get("result") if isinstance(data.get("result"), dict) else data
        return {
            "provider": "seedance",
            "provider_task_id": provider_task_id,
            "status": self._extract_status(response, default="completed"),
            "video_url": result.get("video_url") or result.get("output_url") or result.get("video_path"),
            "raw_result": result,
        }

    def _build_seedance_payload(self, generation_task: GenerationTask) -> dict[str, Any]:
        request_payload = generation_task.request_payload or {}
        assets = request_payload.get("assets", [])
        return {
            "generation_mode": request_payload.get("generation_mode", ""),
            "prompt": request_payload.get("prompt", ""),
            "negative_prompt": request_payload.get("negative_prompt", ""),
            "directives": {
                "camera": request_payload.get("camera", ""),
                "motion": request_payload.get("motion", ""),
                "lighting": request_payload.get("lighting", ""),
            },
            "asset_references": [
                {
                    "asset_id": asset.get("asset_id"),
                    "asset_type": asset.get("asset_type"),
                    "role": asset.get("role"),
                    "reference_tag": asset.get("reference_tag"),
                    "file_path": asset.get("file_path"),
                    "status": asset.get("status"),
                }
                for asset in assets
            ],
            "metadata": {
                "generation_task_id": generation_task.task_id,
                "production_task_id": request_payload.get("production_task_id"),
                "shot_id": request_payload.get("shot_id"),
                "model": request_payload.get("model", "seedance"),
            },
        }

    def _request(self, method: str, path: str, json: Optional[dict[str, Any]] = None) -> dict[str, Any]:
        if not self.api_key:
            raise VideoProviderError("SEEDANCE_API_KEY is not configured.")
        if not self.base_url:
            raise VideoProviderError("SEEDANCE_BASE_URL is not configured.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        if self.http_client is not None:
            try:
                response = self.http_client.request(method, path, json=json, headers=headers)
            except httpx.HTTPError as exc:
                raise VideoProviderError(f"Seedance request failed: {exc}") from exc
        else:
            try:
                with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
                    response = client.request(method, path, json=json, headers=headers)
            except httpx.HTTPError as exc:
                raise VideoProviderError(f"Seedance request failed: {exc}") from exc

        if response.status_code >= 400:
            detail = response.text.strip() or f"HTTP {response.status_code}"
            raise VideoProviderError(f"Seedance API error: {detail}")

        try:
            body = response.json()
        except ValueError as exc:
            raise VideoProviderError("Seedance API returned non-JSON response.") from exc

        if not isinstance(body, dict):
            raise VideoProviderError("Seedance API returned an invalid response payload.")

        return body

    def _get_provider_task_id(self, generation_task: GenerationTask) -> str:
        provider_request = generation_task.request_payload.get("provider_request", {})
        provider_task_id = provider_request.get("provider_task_id")
        if not provider_task_id:
            raise VideoProviderError("Missing provider task id for Seedance provider request.")
        return str(provider_task_id)

    def _extract_provider_task_id(self, response: dict[str, Any]) -> str:
        data = self._extract_data(response)
        provider_task_id = data.get("task_id") or data.get("id") or response.get("task_id") or response.get("id")
        if not provider_task_id:
            raise VideoProviderError("Seedance create_task response did not include a task id.")
        return str(provider_task_id)

    def _extract_status(self, response: dict[str, Any], default: str = "") -> str:
        data = self._extract_data(response)
        status = data.get("status") or response.get("status") or default
        if not status:
            raise VideoProviderError("Seedance response did not include a status.")
        return str(status)

    def _extract_data(self, response: dict[str, Any]) -> dict[str, Any]:
        data = response.get("data")
        if isinstance(data, dict):
            return data
        return response
