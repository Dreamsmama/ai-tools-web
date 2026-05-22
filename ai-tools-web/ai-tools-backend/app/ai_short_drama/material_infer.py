from __future__ import annotations

from typing import Dict, List

ROLE_CN_TO_KEY: Dict[str, str] = {
    "程序员": "programmer",
    "产品经理": "product_manager",
    "hr": "hr",
    "HR": "hr",
    "测试": "tester",
    "运维": "devops",
    "销售": "sales",
    "设计师": "ui",
    "ui设计师": "ui",
    "UI设计师": "ui",
    "视觉设计": "ui",
    "运营": "operations",
}

EMOTION_CN_TO_KEY: Dict[str, str] = {
    "平静": "calm",
    "冷静": "calm",
    "疲惫": "tired",
    "累": "tired",
    "紧张": "stressed",
    "压力": "stressed",
    "压抑": "stressed",
    "震惊": "shocked",
    "懵": "shocked",
    "愤怒": "angry",
    "生气": "angry",
    "开心": "happy",
    "高兴": "happy",
    "苦笑": "normal",
    "释然": "happy",
    "沉默": "normal",
    "真实": "normal",
    "搞笑": "happy",
    "扎心": "stressed",
    "反转": "shocked",
}

# 标准场景枚举（AI 输出与素材库对齐）
SCENE_CN_TO_KEY: Dict[str, str] = {
    "深夜办公室": "night_office",
    "深夜工位": "night_office",
    "办公室": "office_day",
    "白天办公室": "office_day",
    "夜间办公室": "office_night",
    "工位": "desk",
    "工作站": "workstation",
    "会议室": "meeting_room",
    "面试": "interview_room",
    "面试间": "interview_room",
    "机房": "server_room",
    "服务器": "server_room",
}

SCENE_KEYWORDS: Dict[str, List[str]] = {
    "night_office": [
        "深夜",
        "晚上",
        "night",
        "night_office",
        "office_night",
        "subway",
        "metro",
        "commute",
        "便利店",
        "雨夜",
    ],
    "office_night": ["夜间", "office_night", "night_office", "elevator", "电梯", "外景"],
    "office_day": ["白天", "office_day", "明亮", "通勤", "早高峰", "公交"],
    "office": ["办公室", "office"],
    "meeting_room": ["会议", "meeting", "meeting_room", "白板", "whiteboard"],
    "desk": ["工位", "desk", "feishu", "jira", "消息"],
    "workstation": ["工作站", "workstation", "电脑桌"],
    "interview_room": ["面试", "interview"],
    "server_room": ["机房", "服务器", "server", "报警", "oncall", "运维", "终端", "terminal"],
}

# 旧值兼容映射
SCENE_LEGACY_ALIASES: Dict[str, str] = {
    "office": "office_day",
    "night": "night_office",
    "meeting": "meeting_room",
    "interview": "interview_room",
}

SCENE_MATCH_GROUPS: Dict[str, List[str]] = {
    "night_office": ["night_office", "office_night", "night", "late"],
    "office_night": ["office_night", "night_office", "night", "late"],
    "office_day": ["office_day", "office", "workplace"],
    "office": ["office", "office_day", "workplace"],
    "meeting_room": ["meeting_room", "meeting"],
    "desk": ["desk", "workstation", "工位"],
    "workstation": ["workstation", "desk", "工位"],
    "server_room": ["server_room", "server", "alert", "oncall"],
    "interview_room": ["interview_room", "interview"],
}


def normalize_tags(tags: List[str]) -> List[str]:
    return [str(t).strip().lower() for t in tags if str(t).strip()]


def infer_role_key(role_text: str) -> str:
    """将段落 role 字段解析为 roleKey；仅精确匹配，不做子串猜测。"""
    from app.ai_short_drama.role_catalog import resolve_role_key

    text = (role_text or "").strip()
    if not text:
        return "none"
    if text in ROLE_CN_TO_KEY:
        return ROLE_CN_TO_KEY[text]
    resolved = resolve_role_key(text, text)
    if resolved and resolved != "programmer":
        return resolved
    low = text.lower()
    try:
        from app.ai_short_drama.profession_store import profession_store

        if profession_store.is_valid_role(low):
            return low
    except Exception:
        pass
    if low in ROLE_CN_TO_KEY.values():
        return low
    return low if low else "none"


def infer_emotion_key(emotion_text: str) -> str:
    text = (emotion_text or "").strip()
    if not text:
        return "none"
    if text in EMOTION_CN_TO_KEY:
        return EMOTION_CN_TO_KEY[text]
    for cn, key in EMOTION_CN_TO_KEY.items():
        if cn in text:
            return key
    low = text.lower()
    if low in ("calm", "tired", "stressed", "normal", "happy", "shocked", "angry", "confused"):
        return low
    return "none"


def infer_scene_key(scene_text: str) -> str:
    text = (scene_text or "").strip()
    if not text:
        return "none"
    if text in SCENE_CN_TO_KEY:
        return SCENE_CN_TO_KEY[text]
    for cn, key in SCENE_CN_TO_KEY.items():
        if cn in text:
            return key
    low = text.lower().replace("-", "_")
    if low in SCENE_LEGACY_ALIASES:
        return SCENE_LEGACY_ALIASES[low]
    if low in SCENE_KEYWORDS or low in SCENE_CN_TO_KEY.values():
        return low
    for key, kws in SCENE_KEYWORDS.items():
        if any(k in text or k in low for k in kws):
            return key
    return "none"


def normalize_scene_key(scene_text: str) -> str:
    """归一化场景 key；无法识别时默认 night_office（减少白天工位壁纸感）。"""
    key = infer_scene_key(scene_text)
    if key == "none":
        return "night_office"
    if key in SCENE_LEGACY_ALIASES:
        return SCENE_LEGACY_ALIASES[key]
    return key


def scene_match_keys(scene_key: str) -> List[str]:
    key = normalize_scene_key(scene_key)
    return SCENE_MATCH_GROUPS.get(key, [key] if key != "none" else ["office_day"])
