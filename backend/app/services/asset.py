"""Asset management service."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from uuid import uuid4

from app.models.asset import Asset
from app.repositories.asset import AssetRepository
from app.repositories.production import ProductionRepository


ALLOWED_ASSET_STATUSES = {"pending", "uploaded", "approved", "rejected"}


class AssetUploadError(Exception):
    """Raised when an asset upload cannot be completed."""


class AssetNotFoundError(Exception):
    """Raised when an asset cannot be found."""


class AssetStatusError(Exception):
    """Raised when an asset status change is invalid."""


class ProductionTaskAssetError(Exception):
    """Raised when a production task for asset operations cannot be found."""


@dataclass
class AssetService:
    """Manage asset uploads and state transitions."""

    asset_repository: AssetRepository
    production_repository: ProductionRepository
    storage_dir: Path

    def upload_asset(
        self,
        production_task_id: str,
        role: str,
        reference_tag: str,
        requirement_note: str,
        filename: str,
        content: bytes,
        content_type: str = "",
    ) -> Asset:
        production_task = self.production_repository.get_by_id(production_task_id)
        if production_task is None:
            raise ProductionTaskAssetError(f"ProductionTask {production_task_id} not found.")

        if not content:
            raise AssetUploadError("Uploaded file is empty.")

        asset = self.asset_repository.get_by_task_role_reference(
            production_task_id=production_task_id,
            role=role,
            reference_tag=reference_tag,
        )
        file_path = self._save_file(production_task_id, filename, content)

        if asset is None:
            asset = self.asset_repository.create(
                shot_id=production_task.shot_id,
                production_task_id=production_task_id,
                asset_type=self._infer_asset_type(filename, content_type),
                role=role,
                reference_tag=reference_tag,
                requirement_note=requirement_note,
                file_path=file_path,
                status="uploaded",
            )
        else:
            asset = self.asset_repository.update(
                asset.asset_id,
                requirement_note=requirement_note,
                file_path=file_path,
                status="uploaded",
            )
            if asset is None:
                raise AssetUploadError("Asset could not be updated after upload.")

        self._sync_production_task_status(production_task_id)
        return asset

    def list_assets(self, production_task_id: str) -> list[Asset]:
        production_task = self.production_repository.get_by_id(production_task_id)
        if production_task is None:
            raise ProductionTaskAssetError(f"ProductionTask {production_task_id} not found.")

        return self.asset_repository.list_by_production_task_id(production_task_id)

    def update_asset_status(self, asset_id: str, status: str) -> Asset:
        if status not in ALLOWED_ASSET_STATUSES:
            raise AssetStatusError(f"Unsupported asset status: {status}.")

        asset = self.asset_repository.get_by_id(asset_id)
        if asset is None:
            raise AssetNotFoundError(f"Asset {asset_id} not found.")

        updated_asset = self.asset_repository.update(asset_id, status=status)
        if updated_asset is None:
            raise AssetNotFoundError(f"Asset {asset_id} not found.")

        if updated_asset.production_task_id:
            self._sync_production_task_status(updated_asset.production_task_id)

        return updated_asset

    def _save_file(self, production_task_id: str, filename: str, content: bytes) -> str:
        safe_name = Path(filename or "upload.bin").name
        target_dir = self.storage_dir / production_task_id
        target_dir.mkdir(parents=True, exist_ok=True)
        target_path = target_dir / f"{uuid4()}_{safe_name}"
        target_path.write_bytes(content)
        return str(target_path)

    @staticmethod
    def _infer_asset_type(filename: str, content_type: str) -> str:
        suffix = Path(filename).suffix.lower()
        image_suffixes = {".png", ".jpg", ".jpeg", ".webp"}
        video_suffixes = {".mp4", ".mov", ".m4v"}
        audio_suffixes = {".mp3", ".wav", ".m4a"}

        if content_type.startswith("image/") or suffix in image_suffixes:
            return "reference_image"
        if content_type.startswith("video/") or suffix in video_suffixes:
            return "reference_video"
        if content_type.startswith("audio/") or suffix in audio_suffixes:
            return "audio"

        raise AssetUploadError(f"Unsupported uploaded asset type for file: {filename}.")

    def _sync_production_task_status(self, production_task_id: str) -> None:
        production_task = self.production_repository.get_by_id(production_task_id)
        if production_task is None:
            return

        assets = self.asset_repository.list_by_production_task_id(production_task_id)
        if not assets:
            return

        next_status = "ready" if all(asset.status == "approved" for asset in assets) else "waiting_asset"
        self.production_repository.update(production_task_id, status=next_status)
