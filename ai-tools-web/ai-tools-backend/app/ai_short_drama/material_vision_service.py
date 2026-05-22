from __future__ import annotations

import base64
import json
import logging
import mimetypes
from typing import Any, Dict, List

import httpx

from app.ai_short_drama.json_parse import try_parse_json_array
from app.config import settings
from app.utils.llm_json import try_parse_json_object

logger = logging.getLogger(__name__)

DASHSCOPE_VISION_URL = (
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
)
DASHSCOPE_VISION_MODEL = "qwen-vl-plus"

VALID_ROLES = frozenset(
    {"programmer", "product_manager", "hr", "tester", "devops", "sales"}
)
VALID_EMOTIONS = frozenset(
    {"normal", "tired", "stressed", "shocked", "angry", "happy", "confused", "none"}
)
VALID_SCENES = frozenset(
    {
        "night_office",
        "meeting_room",
        "desk",
        "interview_room",
        "server_room",
        "office",
        "none",
    }
)
VALID_TYPES = frozenset({"character", "scene", "ui", "placeholder"})

ROLE_LABELS = {
    "programmer": "程序员素材",
    "product_manager": "产品经理素材",
    "hr": "HR素材",
    "tester": "测试素材",
    "devops": "运维素材",
    "sales": "销售素材",
}


def _guess_mime(filename: str) -> str:
    mime, _ = mimetypes.guess_type(filename)
    return mime or "image/jpeg"


def _image_data_url(content: bytes, filename: str) -> str:
    mime = _guess_mime(filename)
    b64 = base64.b64encode(content).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _build_vision_messages(image_data_url: str, user_role: str) -> List[Dict[str, Any]]:
    prompt = f"""
你是职场短剧素材库的标注助手。请分析这张人物/场景图片，输出用于素材检索的结构化 JSON。

用户已指定职业角色 role 必须为：{user_role}（不要改成别的）。

只返回一个 JSON 对象，不要 markdown，字段：
{{
  "name": "简短中文名，如 疲惫程序员",
  "type": "character",
  "role": "{user_role}",
  "emotion": "只能从 normal,tired,stressed,shocked,angry,happy,confused,none 中选一个",
  "scene": "只能从 night_office,meeting_room,desk,interview_room,server_room,office,none 中选一个",
  "description": "一句中文描述画面",
  "tags": ["英文小写标签数组，5-8个，含 character 与 role 相关词"]
}}

规则：
- type 默认 character
- role 必须是 {user_role}
- tags 用英文小写，适合素材匹配
"""
    return [
        {
            "role": "user",
            "content": [
                {"image": image_data_url},
                {"text": prompt.strip()},
            ],
        }
    ]


async def _call_vision_api(messages: List[Dict[str, Any]]) -> str:
    api_key = settings.dashscope_api_key.strip()
    if not api_key:
        raise RuntimeError("缺少 DASHSCOPE_API_KEY 环境变量")

    payload = {
        "model": DASHSCOPE_VISION_MODEL,
        "input": {"messages": messages},
        "parameters": {"temperature": 0.2, "max_tokens": 800},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    timeout = httpx.Timeout(max(settings.dashscope_timeout_seconds, 45.0))

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(DASHSCOPE_VISION_URL, json=payload, headers=headers)
        resp.raise_for_status()
        body = resp.json()

    content = None
    try:
        choices = body.get("output", {}).get("choices") or []
        if choices:
            msg = choices[0].get("message") or {}
            content = msg.get("content")
        if content is None:
            content = body.get("output", {}).get("text")
    except (TypeError, IndexError, AttributeError):
        content = None

    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict) and part.get("text"):
                parts.append(str(part["text"]))
            elif isinstance(part, str):
                parts.append(part)
        content = "\n".join(parts)

    if not content:
        snippet = json.dumps(body, ensure_ascii=False)[:500]
        raise RuntimeError(f"视觉模型返回为空：{snippet}")
    return content if isinstance(content, str) else str(content)


def _normalize_tags(raw: Any, meta: Dict[str, Any]) -> List[str]:
    tags: List[str] = []
    if isinstance(raw, list):
        for t in raw:
            n = str(t).strip().lower()
            if n and n not in tags:
                tags.append(n)
    for key in ("type", "role", "emotion", "scene"):
        v = str(meta.get(key) or "").strip().lower()
        if v and v != "none" and v not in tags:
            tags.append(v)
    if meta.get("type") == "character" and "character" not in tags:
        tags.insert(0, "character")
    return tags[:12]


def _pick_enum(value: Any, allowed: frozenset, default: str) -> str:
    v = str(value or "").strip().lower()
    return v if v in allowed else default


def fallback_metadata(user_role: str, user_name: str = "") -> Dict[str, Any]:
    role = _pick_enum(user_role, VALID_ROLES, "programmer")
    name = (user_name or "").strip() or ROLE_LABELS.get(role, "人物素材")
    return {
        "name": name,
        "type": "character",
        "role": role,
        "emotion": "normal",
        "scene": "office",
        "description": f"{name}，职场人物场景素材",
        "tags": ["character", role, "normal", "office"],
        "source": "fallback",
    }


def normalize_vision_metadata(
    raw_obj: Dict[str, Any],
    *,
    user_role: str,
    user_name: str = "",
) -> Dict[str, Any]:
    role = _pick_enum(user_role, VALID_ROLES, "programmer")
    emotion = _pick_enum(raw_obj.get("emotion"), VALID_EMOTIONS, "normal")
    scene = _pick_enum(raw_obj.get("scene"), VALID_SCENES, "office")
    mtype = _pick_enum(raw_obj.get("type"), VALID_TYPES, "character")
    if mtype != "character":
        mtype = "character"

    ai_name = str(raw_obj.get("name") or "").strip()
    name = (user_name or "").strip() or ai_name or ROLE_LABELS.get(role, "人物素材")

    meta = {
        "name": name[:40],
        "type": mtype,
        "role": role,
        "emotion": emotion,
        "scene": scene,
        "description": str(raw_obj.get("description") or "").strip()[:200],
        "tags": _normalize_tags(raw_obj.get("tags"), {
            "type": mtype,
            "role": role,
            "emotion": emotion,
            "scene": scene,
        }),
        "source": "ai",
    }
    return meta


def parse_vision_output(raw: str, user_role: str, user_name: str = "") -> Dict[str, Any]:
    obj = try_parse_json_object(raw)
    if obj is None:
        arr = try_parse_json_array(raw)
        if arr and isinstance(arr[0], dict):
            obj = arr[0]
    if obj is None:
        raise ValueError("无法解析视觉模型 JSON")
    return normalize_vision_metadata(obj, user_role=user_role, user_name=user_name)


async def analyze_material_image(
    content: bytes,
    filename: str,
    user_role: str,
    user_name: str = "",
) -> Dict[str, Any]:
    role = _pick_enum(user_role, VALID_ROLES, "")
    if not role:
        raise ValueError("请选择职业角色")

    try:
        data_url = _image_data_url(content, filename)
        messages = _build_vision_messages(data_url, role)
        raw = await _call_vision_api(messages)
        return parse_vision_output(raw, user_role=role, user_name=user_name)
    except Exception as err:
        logger.warning("material vision analyze failed, fallback: %s", err)
        return fallback_metadata(role, user_name)
