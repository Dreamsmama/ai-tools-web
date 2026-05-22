"""Tests for deterministic xiaohongshu output validation (R5)."""

from app.schemas import XiaohongshuAgentData
from app.validators.content_output import validate_xiaohongshu_output


def test_drops_sensitive_title():
    raw = XiaohongshuAgentData(
        titles=["这是最好的产品", "正常标题"],
        content="正文",
        image_prompts=["图"],
        publish_tips=[],
        risks=[],
    )
    data, fixes = validate_xiaohongshu_output(raw, 3)
    assert "正常标题" in data.titles
    assert not any("最好" in t for t in data.titles)
    assert "default_publish_tips" in fixes
    assert "default_risks" in fixes


def test_truncates_long_title():
    raw = XiaohongshuAgentData(
        titles=["a" * 50],
        content="x",
        image_prompts=[],
        publish_tips=["tip"],
        risks=["risk"],
    )
    data, _ = validate_xiaohongshu_output(raw, 1)
    assert len(data.titles[0]) <= 30


def test_strips_sensitive_in_content():
    raw = XiaohongshuAgentData(
        titles=["标题"],
        content="百分百有效的好物推荐",
        image_prompts=[],
        publish_tips=["已有"],
        risks=["已有"],
    )
    data, fixes = validate_xiaohongshu_output(raw, 1)
    assert "百分百" not in data.content
    assert "content_stripped_sensitive" in fixes
