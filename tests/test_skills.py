"""The skills meet the strictest install target, claude.ai (nstarman/skills checks the same)."""

import re
from pathlib import Path

import pytest
import yaml

SKILLS = sorted((Path(__file__).parents[1] / "skills").iterdir())


@pytest.mark.parametrize("skill", SKILLS, ids=lambda p: p.name)
def test_frontmatter(skill):
    text = (skill / "SKILL.md").read_text(encoding="utf-8")
    front = yaml.safe_load(text.split("---")[1])
    assert front["name"] == skill.name
    assert re.fullmatch(r"[a-z0-9-]{1,64}", front["name"])
    assert len(front["description"]) <= 1024


def test_both_skills_exist():
    assert [p.name for p in SKILLS] == ["syw-site", "syw-site-upgrade"]


def test_references_resolve():
    skill = Path(__file__).parents[1] / "skills" / "syw-site"
    for ref in re.findall(r"\]\((references/[^)]+)\)", (skill / "SKILL.md").read_text()):
        assert (skill / ref).exists(), ref
