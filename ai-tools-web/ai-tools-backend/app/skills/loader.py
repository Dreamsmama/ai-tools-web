"""Load SKILL.md bodies for prompt assembly."""

from __future__ import annotations

import re
from pathlib import Path

_SKILLS_DIR = Path(__file__).resolve().parent
_FRONTMATTER = re.compile(r"^---\s*\n.*?\n---\s*\n", re.DOTALL)


def load_skill_markdown(skill_name: str) -> str:
    """Read ``<skill_name>/SKILL.md`` and strip optional YAML frontmatter."""
    path = _SKILLS_DIR / skill_name / "SKILL.md"
    if not path.is_file():
        raise FileNotFoundError(f"Skill not found: {path}")
    text = path.read_text(encoding="utf-8").strip()
    text = _FRONTMATTER.sub("", text, count=1).strip()
    return text
