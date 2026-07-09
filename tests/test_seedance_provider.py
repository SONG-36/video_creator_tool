"""Seedance provider tests."""

from __future__ import annotations

import json

import httpx
import pytest

from app.models.generation_task import GenerationTask
from app.providers.seedance_provider import SeedanceProvider
from app.providers.video_provider import VideoProviderError


def build_generation_task() -> GenerationTask:
    return GenerationTask(
        task_id="gen-task-1",
        production_task_id="prod-task-1",
        provider="seedance",
        status="pending",
        request_payload={
            "production_task_id": "prod-task-1",
            "shot_id": "shot-1",
            "model": "seedance",
            "generation_mode": "i2v",
            "prompt": "Show the bottle cleaning the stain.",
            "negative_prompt": "blur, flicker",
            "camera": "Side dolly to packshot.",
            "motion": "Foam sweeps across frame.",
            "lighting": "Soft daylight with specular highlights.",
            "assets": [
                {
                    "asset_id": "asset-1",
                    "asset_type": "product_image",
                    "role": "identity_reference",
                    "reference_tag": "@Image1",
                    "file_path": "storage/assets/product.png",
                    "status": "approved",
                },
                {
                    "asset_id": "asset-2",
                    "asset_type": "reference_video",
                    "role": "motion_reference",
                    "reference_tag": "@Video1",
                    "file_path": "storage/assets/motion.mp4",
                    "status": "approved",
                },
            ],
        },
        result_payload=None,
        error_message="",
    )


def test_seedance_provider_create_task_formats_request_payload() -> None:
    captured: dict[str, object] = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["method"] = request.method
        captured["url"] = str(request.url)
        captured["authorization"] = request.headers.get("Authorization")
        captured["payload"] = json.loads(request.content.decode("utf-8"))
        return httpx.Response(
            200,
            json={"data": {"task_id": "seedance-task-1", "status": "queued"}},
        )

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://seedance.test",
    )
    provider = SeedanceProvider(
        base_url="https://seedance.test",
        api_key="seedance-secret",
        http_client=client,
    )

    response = provider.create_task(build_generation_task())

    assert response["provider"] == "seedance"
    assert response["provider_task_id"] == "seedance-task-1"
    assert response["accepted"] is True
    assert captured["method"] == "POST"
    assert captured["url"] == "https://seedance.test/tasks"
    assert captured["authorization"] == "Bearer seedance-secret"

    payload = captured["payload"]
    assert isinstance(payload, dict)
    assert payload["generation_mode"] == "i2v"
    assert payload["prompt"] == "Show the bottle cleaning the stain."
    assert payload["negative_prompt"] == "blur, flicker"
    assert payload["directives"]["camera"] == "Side dolly to packshot."
    assert payload["directives"]["motion"] == "Foam sweeps across frame."
    assert payload["directives"]["lighting"] == "Soft daylight with specular highlights."
    assert payload["asset_references"][0]["role"] == "identity_reference"
    assert payload["asset_references"][1]["reference_tag"] == "@Video1"
    assert payload["metadata"]["generation_task_id"] == "gen-task-1"

    client.close()


def test_seedance_provider_get_status_maps_remote_status() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert str(request.url) == "https://seedance.test/tasks/seedance-task-1"
        return httpx.Response(200, json={"data": {"task_id": "seedance-task-1", "status": "processing"}})

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://seedance.test",
    )
    provider = SeedanceProvider(
        base_url="https://seedance.test",
        api_key="seedance-secret",
        http_client=client,
    )

    generation_task = build_generation_task()
    generation_task.request_payload["provider_request"] = {"provider_task_id": "seedance-task-1"}

    assert provider.get_status(generation_task) == "running"

    client.close()


def test_seedance_provider_get_result_returns_normalized_payload() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.method == "GET"
        assert str(request.url) == "https://seedance.test/tasks/seedance-task-1/result"
        return httpx.Response(
            200,
            json={
                "data": {
                    "task_id": "seedance-task-1",
                    "status": "completed",
                    "video_url": "https://cdn.seedance.test/videos/final.mp4",
                    "thumbnail_url": "https://cdn.seedance.test/videos/final.jpg",
                }
            },
        )

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://seedance.test",
    )
    provider = SeedanceProvider(
        base_url="https://seedance.test",
        api_key="seedance-secret",
        http_client=client,
    )

    generation_task = build_generation_task()
    generation_task.request_payload["provider_request"] = {"provider_task_id": "seedance-task-1"}

    result = provider.get_result(generation_task)

    assert result["provider"] == "seedance"
    assert result["provider_task_id"] == "seedance-task-1"
    assert result["status"] == "completed"
    assert result["video_url"] == "https://cdn.seedance.test/videos/final.mp4"
    assert result["raw_result"]["thumbnail_url"] == "https://cdn.seedance.test/videos/final.jpg"

    client.close()


def test_seedance_provider_raises_on_api_failure() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, json={"detail": "rate limit"})

    client = httpx.Client(
        transport=httpx.MockTransport(handler),
        base_url="https://seedance.test",
    )
    provider = SeedanceProvider(
        base_url="https://seedance.test",
        api_key="seedance-secret",
        http_client=client,
    )

    with pytest.raises(VideoProviderError) as exc:
        provider.create_task(build_generation_task())

    assert "Seedance API error" in str(exc.value)
    assert "rate limit" in str(exc.value)

    client.close()
