"""
Contract tests for xiaohongshu five-step agent (R4).

Mocks ``call_dashscope`` so tests run offline without API keys.
"""

from __future__ import annotations

import json
import re
import unittest
from typing import Any, List
from unittest.mock import patch

from app.agents.xiaohongshu.spec import LLM_PIPELINE, pipeline_step_ids, step_labels
from app.services.xiaohongshu_agent_service import xiaohongshu_agent_service
from app.services.xiaohongshu_agent_sse import format_sse_message

_ANALYSIS_JSON = json.dumps(
    {
        "topic_focus": "职场成长",
        "value_points": ["真实体验"],
        "audience_insights": ["年轻白领"],
        "tone_guidance": ["真诚"],
        "style": "种草",
    },
    ensure_ascii=False,
)

_PLAN_JSON = json.dumps(
    {
        "positioning": "打工人成长记录",
        "outline": ["开头", "价值", "行动"],
        "title_angles": ["角度A"],
        "count": 2,
    },
    ensure_ascii=False,
)

_COPY_JSON = json.dumps(
    {
        "titles": ["今晚适合慢下来的小事", "打工人下班瞬间"],
        "content": "这是可发布的正文，结构清楚，并有行动引导。",
    },
    ensure_ascii=False,
)

_IMAGE_JSON = json.dumps(
    {"image_prompts": ["竖屏生活场景，暖光", "书桌与咖啡，治愈风"]},
    ensure_ascii=False,
)

_RISK_JSON = json.dumps(
    {
        "publish_tips": ["发布前核对事实"],
        "risks": ["避免绝对化用语"],
    },
    ensure_ascii=False,
)


def _system_text(messages: List[dict[str, str]]) -> str:
    return (messages[0].get("content") or "") if messages else ""


async def _mock_call_dashscope_success(
    messages: List[dict[str, str]],
    **_: Any,
) -> str:
    system = _system_text(messages)
    if "内容策略" in system:
        return _ANALYSIS_JSON
    if "内容规划" in system:
        return _PLAN_JSON
    if "小红书文案" in system:
        return _COPY_JSON
    if "图片提示词" in system:
        return _IMAGE_JSON
    if "合规" in system:
        return _RISK_JSON
    raise AssertionError(f"unexpected mock call, system={system[:80]!r}")


async def _mock_call_dashscope_bad_json(
    messages: List[dict[str, str]],
    **_: Any,
) -> str:
    system = _system_text(messages)
    if "内容策略" in system:
        return _ANALYSIS_JSON
    if "内容规划" in system:
        return _PLAN_JSON
    if "小红书文案" in system:
        return "not valid json {{"
    return _RISK_JSON


async def _mock_call_dashscope_empty_copy(
    messages: List[dict[str, str]],
    **_: Any,
) -> str:
    system = _system_text(messages)
    if "内容策略" in system:
        return _ANALYSIS_JSON
    if "内容规划" in system:
        return _PLAN_JSON
    if "小红书文案" in system:
        return json.dumps({"titles": [], "content": ""}, ensure_ascii=False)
    if "图片提示词" in system:
        return json.dumps({"image_prompts": []}, ensure_ascii=False)
    if "合规" in system:
        return json.dumps({"publish_tips": [], "risks": []}, ensure_ascii=False)
    raise AssertionError("unexpected mock call")


class XiaohongshuAgentContractTest(unittest.IsolatedAsyncioTestCase):
    @patch(
        "app.agents.xiaohongshu.steps.call_dashscope",
        side_effect=_mock_call_dashscope_success,
    )
    async def test_run_success_five_steps(self, _mock: Any) -> None:
        envelope = await xiaohongshu_agent_service.run(
            topic="职场倦怠怎么办",
            product="",
            audience="打工人",
            style="种草",
            count=2,
        )
        self.assertEqual(0, envelope.code)
        self.assertIsNotNone(envelope.data)
        assert envelope.data is not None
        self.assertEqual(2, len(envelope.data.titles))
        self.assertTrue(envelope.data.content.strip())
        self.assertEqual(2, len(envelope.data.image_prompts))
        self.assertTrue(envelope.data.publish_tips)
        self.assertTrue(envelope.data.risks)
        self.assertEqual(5, _mock.await_count)

    async def test_empty_topic_returns_400(self) -> None:
        envelope = await xiaohongshu_agent_service.run(
            topic="  ",
            product="",
            audience="",
            style="种草",
            count=3,
        )
        self.assertEqual(400, envelope.code)

    @patch(
        "app.agents.xiaohongshu.steps.call_dashscope",
        side_effect=_mock_call_dashscope_bad_json,
    )
    async def test_invalid_json_returns_500(self, _mock: Any) -> None:
        envelope = await xiaohongshu_agent_service.run(
            topic="测试主题",
            product="",
            audience="",
            style="干货",
            count=2,
        )
        self.assertEqual(500, envelope.code)
        self.assertIn("格式", envelope.message or "")

    @patch(
        "app.agents.xiaohongshu.steps.call_dashscope",
        side_effect=_mock_call_dashscope_empty_copy,
    )
    async def test_empty_generation_returns_500(self, _mock: Any) -> None:
        envelope = await xiaohongshu_agent_service.run(
            topic="测试主题",
            product="",
            audience="",
            style="测评",
            count=2,
        )
        self.assertEqual(500, envelope.code)
        self.assertIn("未生成", envelope.message or "")

    @patch(
        "app.agents.xiaohongshu.steps.call_dashscope",
        side_effect=_mock_call_dashscope_success,
    )
    async def test_sensitive_title_removed_by_validator(self, _mock: Any) -> None:
        async def mock_with_sensitive(
            messages: List[dict[str, str]],
            **kwargs: Any,
        ) -> str:
            system = _system_text(messages)
            if "小红书文案" in system:
                return json.dumps(
                    {
                        "titles": ["这是最好的产品", "正常标题"],
                        "content": "正文内容足够长，用于通过校验与展示。",
                    },
                    ensure_ascii=False,
                )
            return await _mock_call_dashscope_success(messages, **kwargs)

        _mock.side_effect = mock_with_sensitive
        envelope = await xiaohongshu_agent_service.run(
            topic="好物分享",
            product="",
            audience="",
            style="种草",
            count=3,
        )
        self.assertEqual(0, envelope.code)
        assert envelope.data is not None
        self.assertNotIn("这是最好的产品", envelope.data.titles)
        self.assertIn("正常标题", envelope.data.titles)

    @patch(
        "app.agents.xiaohongshu.steps.call_dashscope",
        side_effect=_mock_call_dashscope_success,
    )
    async def test_iter_sse_emits_progress_and_result(self, _mock: Any) -> None:
        chunks: list[str] = []
        async for chunk in xiaohongshu_agent_service.iter_sse(
            topic="职场倦怠怎么办",
            product="",
            audience="打工人",
            style="种草",
            count=2,
            generate_images=False,
        ):
            chunks.append(chunk)

        progress_events = [
            c for c in chunks if c.startswith("event: progress")
        ]
        result_events = [c for c in chunks if c.startswith("event: result")]
        self.assertGreaterEqual(len(progress_events), 5)
        self.assertEqual(1, len(result_events))

        first = progress_events[0]
        data_match = re.search(r"^data:\s*(.+)$", first, re.MULTILINE)
        self.assertIsNotNone(data_match)
        payload = json.loads(data_match.group(1))
        self.assertEqual("step", payload["type"])
        self.assertEqual("start", payload["phase"])
        self.assertEqual(1, payload["index"])
        self.assertEqual(5, payload["total"])

        result_data = re.search(r"^data:\s*(.+)$", result_events[0], re.MULTILINE)
        self.assertIsNotNone(result_data)
        envelope = json.loads(result_data.group(1))
        self.assertEqual(0, envelope["code"])


class XiaohongshuSpecTest(unittest.TestCase):
    def test_llm_pipeline_has_five_steps(self) -> None:
        self.assertEqual(5, len(LLM_PIPELINE))
        self.assertEqual(
            ["topic_analyzer", "content_planner", "copywriter", "image_prompt_generator", "risk_checker"],
            [s.id for s in LLM_PIPELINE],
        )

    def test_pipeline_step_ids_with_optional_image(self) -> None:
        self.assertEqual(5, len(pipeline_step_ids(generate_images=False)))
        self.assertEqual(6, len(pipeline_step_ids(generate_images=True)))
        self.assertEqual("配图生成", step_labels()["image_provider"])


class XiaohongshuSseFormatTest(unittest.TestCase):
    def test_format_sse_message(self) -> None:
        msg = format_sse_message("progress", {"type": "step", "index": 2, "total": 5})
        self.assertIn("event: progress\n", msg)
        self.assertIn('"index": 2', msg)
        self.assertTrue(msg.endswith("\n\n"))


if __name__ == "__main__":
    unittest.main()
