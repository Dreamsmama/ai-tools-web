"""Tests for content_compliance skill (R6)."""

import unittest

from app.skills.content_compliance.code import (
    contains_sensitive,
    find_sensitive_hits,
    scan_copywriting,
    strip_sensitive_phrases,
)
from app.skills.loader import load_skill_markdown


class ContentComplianceSkillTest(unittest.TestCase):
    def test_find_hits(self) -> None:
        self.assertEqual(["最好"], find_sensitive_hits("这是最好的"))

    def test_strip_content(self) -> None:
        self.assertNotIn("百分百", strip_sensitive_phrases("百分百有效"))

    def test_scan_copywriting(self) -> None:
        result = scan_copywriting(
            {"titles": ["最好标题"], "content": "正常正文"},
        )
        self.assertTrue(result["title_has_sensitive"])
        self.assertIn("最好", result["sensitive_hits"])

    def test_load_skill_md(self) -> None:
        text = load_skill_markdown("content_compliance")
        self.assertIn("绝对化", text)
        self.assertFalse(text.startswith("---"))


if __name__ == "__main__":
    unittest.main()
