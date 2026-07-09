"""Skill knowledge adapter tests."""

from pathlib import Path

from app.providers.skill_knowledge import FileSystemSkillKnowledgeAdapter


def test_skill_knowledge_adapter_loads_seedance_files() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    adapter = FileSystemSkillKnowledgeAdapter(repo_root / "skills" / "seedance")

    knowledge = adapter.load_seedance_knowledge()

    assert "Reference Tag Syntax" in knowledge.reference_workflow
    assert "Director Formula" in knowledge.prompt_guidance
    assert "Camera Contract" in knowledge.camera_guidance
    assert "Motion Contract" in knowledge.motion_guidance
