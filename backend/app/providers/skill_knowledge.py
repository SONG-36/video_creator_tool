"""Skill knowledge adapter for Seedance reference files."""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Optional, Protocol


class SkillKnowledgeError(Exception):
    """Raised when Seedance skill knowledge cannot be loaded."""


@dataclass(frozen=True)
class SeedanceKnowledge:
    """Readonly bundle of Seedance knowledge sources."""

    reference_workflow: str
    prompt_guidance: str
    camera_guidance: str
    motion_guidance: str


class SkillKnowledgeAdapter(Protocol):
    """Contract for loading AI-director knowledge without hardcoding it."""

    def load_seedance_knowledge(self) -> SeedanceKnowledge:
        """Return the Seedance knowledge bundle."""


@lru_cache
def _load_seedance_knowledge(seedance_root: str) -> SeedanceKnowledge:
    root = Path(seedance_root)
    required_files = {
        "reference_workflow": root / "reference-workflow.md",
        "prompt_guidance": root / "seedance-prompt" / "SKILL.md",
        "camera_guidance": root / "seedance-camera" / "SKILL.md",
        "motion_guidance": root / "seedance-motion" / "SKILL.md",
    }

    missing = [str(path) for path in required_files.values() if not path.exists()]
    if missing:
        missing_paths = ", ".join(missing)
        raise SkillKnowledgeError(f"Missing Seedance knowledge files: {missing_paths}")

    return SeedanceKnowledge(
        reference_workflow=required_files["reference_workflow"].read_text(encoding="utf-8"),
        prompt_guidance=required_files["prompt_guidance"].read_text(encoding="utf-8"),
        camera_guidance=required_files["camera_guidance"].read_text(encoding="utf-8"),
        motion_guidance=required_files["motion_guidance"].read_text(encoding="utf-8"),
    )


class FileSystemSkillKnowledgeAdapter:
    """Load Seedance knowledge from the local repository skill folder."""

    def __init__(self, seedance_root: Optional[Path] = None) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        self.seedance_root = seedance_root or repo_root / "skills" / "seedance"

    def load_seedance_knowledge(self) -> SeedanceKnowledge:
        return _load_seedance_knowledge(str(self.seedance_root.resolve()))
