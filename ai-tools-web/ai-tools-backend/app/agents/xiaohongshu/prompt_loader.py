"""Load Markdown prompts for xiaohongshu agent steps (R2)."""

from __future__ import annotations

from pathlib import Path

_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def load_prompt(name: str, **variables: object) -> str:
    """
    Load ``prompts/<name>.md`` and substitute ``{key}`` placeholders.

    Uses plain replace (not str.format) so JSON braces in templates stay intact.
    """
    path = _PROMPTS_DIR / f"{name}.md"
    if not path.is_file():
        raise FileNotFoundError(f"Prompt not found: {path}")
    text = path.read_text(encoding="utf-8").strip()
    for key, value in variables.items():
        text = text.replace("{" + key + "}", str(value))
    return text
