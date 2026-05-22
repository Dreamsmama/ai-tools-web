from __future__ import annotations

import re
from typing import Any, Dict, List, Literal, Optional, Tuple

SceneIntent = Literal[
    "opening",
    "communication",
    "work_pressure",
    "fatigue",
    "collapse",
    "emotion",
    "daily_life",
]

VALID_SCENE_INTENTS = frozenset(
    {
        "opening",
        "communication",
        "work_pressure",
        "fatigue",
        "collapse",
        "emotion",
        "daily_life",
    }
)

# 易形成「工位壁纸」的 scene，匹配时降权、 enrich 时优先替换
GENERIC_OFFICE_SCENES = frozenset(
    {
        "office_day",
        "desk",
        "workstation",
        "meeting_room",
        "office",
        "office_night",
    }
)

# 每个 intent 多个视觉变体（轮换，避免全片同一工位）
# scene_key 需在 material_paths.VALID_SCENES 内或走 tag 匹配
VisualVariant = Dict[str, Any]

INTENT_VARIANTS: Dict[SceneIntent, List[VisualVariant]] = {
    "opening": [
        {
            "scene_key": "office_day",
            "tags": ["opening", "empty_office", "wide_shot", "exterior"],
            "scene": "竖屏空旷现代办公室全景，晨光透过玻璃，无人出镜，留白构图，9:16",
            "ui": "竖屏简洁日程空白页，清晨色调",
            "effects": "竖屏清晨城市天际线薄雾",
        },
        {
            "scene_key": "office_night",
            "tags": ["opening", "building_exterior", "night_city", "commute"],
            "scene": "竖屏夜晚办公楼外景，玻璃幕墙灯光，街道虚化，无人出镜",
            "ui": "竖屏天气与通勤时间小组件",
            "effects": "竖屏蓝调城市远景",
        },
        {
            "scene_key": "office_day",
            "tags": ["opening", "elevator", "lobby", "commute"],
            "scene": "竖屏写字楼电梯厅，金属门反光，通勤氛围，不要工位特写",
            "ui": "竖屏打卡或门禁界面",
            "effects": "竖屏电梯楼层指示灯特写",
        },
    ],
    "communication": [
        {
            "scene_key": "meeting_room",
            "tags": ["communication", "whiteboard", "sticky_notes"],
            "scene": "竖屏会议室白板与便利贴，椅子侧影，不要横向全景",
            "ui": "竖屏在线文档协作界面，多人光标",
            "props": "竖屏马克笔与便签特写",
        },
        {
            "scene_key": "meeting_room",
            "tags": ["communication", "ppt", "presentation"],
            "scene": "竖屏投影幕布一角，PPT 色块虚化，会议桌边缘",
            "ui": "竖屏视频会议九宫格头像",
            "props": "竖屏翻页笔与激光笔",
        },
        {
            "scene_key": "desk",
            "tags": ["communication", "feishu", "chat", "phone_call"],
            "scene": "竖屏办公桌上的手机与耳机，屏幕聊天框虚化，非显示器大特写",
            "ui": "竖屏飞书群聊列表，工作讨论语气",
            "props": "竖屏电话听筒与便签",
        },
    ],
    "work_pressure": [
        {
            "scene_key": "night_office",
            "tags": ["work_pressure", "feishu", "red_alert", "notification"],
            "scene": "竖屏深夜办公室远景，手机消息红光，不要工位显示器大特写",
            "ui": "竖屏飞书工作群未读红点，催办消息列表",
            "effects": "竖屏红色通知弹层",
        },
        {
            "scene_key": "night_office",
            "tags": ["work_pressure", "jira", "ticket", "deadline"],
            "scene": "竖屏暗色办公空间，屏幕工单列表反光，无人物脸部",
            "ui": "竖屏 Jira 或工单 backlog 列表，高优先级标红",
            "effects": "竖屏倒计时数字光效",
        },
        {
            "scene_key": "office_night",
            "tags": ["work_pressure", "boss_message", "chat", "deadline"],
            "scene": "竖屏深夜写字楼走廊，手机握持剪影，压迫氛围",
            "ui": "竖屏钉钉/飞书老板私聊窗口，质问语气",
            "effects": "竖屏消息轰炸叠影",
        },
    ],
    "fatigue": [
        {
            "scene_key": "night_office",
            "tags": ["fatigue", "empty_desk", "lamp", "cold_coffee"],
            "scene": "竖屏深夜空工位，台灯暖光，冷掉咖啡杯，疲惫安静",
            "ui": "竖屏加班打卡记录满格",
            "props": "竖屏冷咖啡与眼药水",
        },
        {
            "scene_key": "office_night",
            "tags": ["fatigue", "elevator", "late_night", "empty_office"],
            "scene": "竖屏深夜电梯内镜面，疲惫冷色调，数字楼层显示",
            "ui": "竖屏深夜地铁末班车时刻",
            "props": "竖屏电梯按钮特写",
        },
        {
            "scene_key": "night_office",
            "tags": ["fatigue", "subway", "commute", "metro"],
            "scene": "竖屏深夜地铁车厢，空座，窗外隧道灯光，打工人通勤",
            "ui": "竖屏地图通勤路线截图",
            "effects": "竖屏地铁轨道流光",
        },
    ],
    "collapse": [
        {
            "scene_key": "server_room",
            "tags": ["collapse", "alert", "server_room", "red_light"],
            "scene": "竖屏机房机柜红灯闪烁，告警氛围，不要横向长廊",
            "ui": "竖屏监控大盘红色告警条",
            "effects": "竖屏红色告警光晕",
        },
        {
            "scene_key": "server_room",
            "tags": ["collapse", "terminal", "error_log", "linux"],
            "scene": "竖屏 Linux 终端红色报错堆栈，黑底绿红字",
            "ui": "竖屏 Grafana/Prometheus 告警界面",
            "effects": "竖屏故障粒子与闪烁",
        },
        {
            "scene_key": "desk",
            "tags": ["collapse", "incident", "oncall", "red_screen"],
            "scene": "竖屏笔记本屏幕红色错误页，键盘边缘，事故氛围",
            "ui": "竖屏 oncall 轮值通知与事故群",
            "effects": "竖屏系统崩溃提示层",
        },
    ],
    "emotion": [
        {
            "scene_key": "night_office",
            "tags": ["emotion", "window", "city_night", "rain"],
            "scene": "竖屏办公室窗边夜景，雨痕玻璃，城市灯光虚化，情绪留白",
            "ui": "竖屏空白备忘录或熄屏手机",
            "effects": "竖屏雨夜窗边光斑",
        },
        {
            "scene_key": "meeting_room",
            "tags": ["emotion", "empty_meeting", "silence"],
            "scene": "竖屏空会议室，椅子拉开，安静压抑，无人",
            "ui": "竖屏已读不回的聊天窗",
            "effects": "竖屏暖色逆光",
        },
        {
            "scene_key": "office_night",
            "tags": ["emotion", "street_night", "reflection"],
            "scene": "竖屏下班街道夜景，路灯与行人剪影，独处感",
            "ui": "竖屏音乐播放器暂停界面",
            "effects": "竖屏霓虹反射",
        },
    ],
    "daily_life": [
        {
            "scene_key": "office_day",
            "tags": ["daily_life", "subway", "metro", "commute"],
            "scene": "竖屏早高峰地铁车厢，握扶手，通勤拥挤感，不要办公室",
            "ui": "竖屏地铁线路图与到站提醒",
            "effects": "竖屏隧道灯光掠过",
        },
        {
            "scene_key": "night_office",
            "tags": ["daily_life", "convenience_store", "late_night"],
            "scene": "竖屏深夜便利店暖光，货架与关东煮蒸汽，治愈疲惫",
            "ui": "竖屏外卖或打车软件界面",
            "props": "竖屏便利店饭团与咖啡",
        },
        {
            "scene_key": "office_night",
            "tags": ["daily_life", "coffee_shop", "street"],
            "scene": "竖屏街角咖啡店窗外，雨夜街道，室内暖光",
            "ui": "竖屏公交到站信息",
            "props": "竖屏纸杯咖啡与耳机",
        },
        {
            "scene_key": "office_day",
            "tags": ["daily_life", "bus", "commute", "city"],
            "scene": "竖屏公交车窗视角，城市街景移动，通勤日常",
            "ui": "竖屏共享单车解锁界面",
            "effects": "竖屏雨天车窗水珠",
        },
    ],
}

INTENT_PREFER_TYPES: Dict[SceneIntent, List[str]] = {
    "opening": ["scene", "props"],
    "communication": ["scene", "props", "ui"],
    "work_pressure": ["scene", "effects", "props"],
    "fatigue": ["scene", "props"],
    "collapse": ["scene", "effects"],
    "emotion": ["scene", "props"],
    "daily_life": ["scene", "props"],
}

_OPENING_PATTERNS = (
    r"很多人觉得",
    r"真正做过",
    r"才知道",
    r"你以为",
    r"其实",
    r"👉",
    r"^很多人",
)
_COMMUNICATION_PATTERNS = (
    r"沟通",
    r"推进",
    r"解释",
    r"协调",
    r"对齐",
    r"会议",
    r"白板",
    r"PPT",
    r"汇报",
    r"需求",
    r"每天都在",
    r"谁都要",
    r"对接",
)
_WORK_PRESSURE_PATTERNS = (
    r"为什么还没",
    r"上线",
    r"催",
    r"deadline",
    r"老板会说",
    r"会说[：:]",
    r"用户要",
    r"改需求",
    r"排期",
    r"飞书",
    r"消息",
    r"群聊",
    r"还没做完",
    r"什么时候",
    r"工单",
)
_FATIGUE_PATTERNS = (
    r"疲惫",
    r"很累",
    r"加班",
    r"深夜",
    r"凌晨",
    r"越来越累",
    r"夹在中间",
    r"背压力",
    r"咖啡",
    r"睡不着",
    r"困",
)
_COLLAPSE_PATTERNS = (
    r"报警",
    r"崩溃",
    r"宕机",
    r"故障",
    r"报错",
    r"红色",
    r"系统突然",
    r"背锅",
    r"oncall",
    r"事故",
    r"挂了",
    r"监控",
)
_EMOTION_PATTERNS = (
    r"不是因为",
    r"不热爱",
    r"如果重新",
    r"还会做",
    r"沉默",
    r"心里",
    r"其实也想",
    r"无奈",
    r"释然",
)
_DAILY_LIFE_PATTERNS = (
    r"通勤",
    r"地铁",
    r"公交",
    r"便利店",
    r"下班",
    r"回家",
    r"租房",
    r"外卖",
    r"打车",
    r"两个小时",
    r"小时地铁",
    r"早高峰",
    r"雨夜",
    r"街边",
)


def _match_any(patterns: tuple[str, ...], text: str) -> bool:
    return any(re.search(p, text) for p in patterns)


def _variant_index(seed: str, modulo: int) -> int:
    if modulo <= 0:
        return 0
    h = sum(ord(c) for c in seed) % 9973
    return h % modulo


def pick_visual_variant(
    intent: SceneIntent,
    text: str,
    *,
    segment_no: int = 1,
    used_scene_keys: Optional[set] = None,
) -> VisualVariant:
    """按 intent + 文案 + 段序号轮换视觉变体，尽量避免连续重复 scene_key。"""
    variants = INTENT_VARIANTS.get(intent) or INTENT_VARIANTS["opening"]
    seed = f"{segment_no}:{text[:48]}"
    idx = _variant_index(seed, len(variants))
    if used_scene_keys:
        for offset in range(len(variants)):
            cand = variants[(idx + offset) % len(variants)]
            sk = str(cand.get("scene_key") or "office_day")
            if sk not in used_scene_keys:
                return cand
    return variants[idx]


def pick_visual_plan(
    intent: SceneIntent,
    text: str,
    *,
    emotion: str = "",
    segment_no: int = 1,
    total_segments: int = 1,
    used_scene_keys: Optional[set] = None,
    role_key: str = "",
    career_cn: str = "",
) -> Dict[str, Any]:
    """返回 scene_key、tags、各类型生图描述（叠加职业视觉关键词）。"""
    from app.ai_short_drama.role_visual_keywords import (
        infer_visual_role_from_text,
        merge_role_intent_generation,
        resolve_visual_role_key,
    )

    visual_role = resolve_visual_role_key(role_key, career_cn)
    inferred = infer_visual_role_from_text(text)
    if inferred and visual_role == "programmer" and inferred != "programmer":
        visual_role = inferred

    variant = pick_visual_variant(
        intent,
        text,
        segment_no=segment_no,
        used_scene_keys=used_scene_keys,
    )
    tags = list(variant.get("tags") or [])
    tags.append(intent)
    em = (emotion or "").strip().lower()
    if em and em not in tags:
        tags.append(em)
    plan: Dict[str, Any] = {
        "sceneIntent": intent,
        "sceneKey": str(variant.get("scene_key") or "office_day"),
        "sceneHints": tags,
        "visualRole": visual_role,
        "generation": {
            "scene": str(variant.get("scene") or ""),
            "ui": str(variant.get("ui") or ""),
            "effects": str(variant.get("effects") or ""),
            "props": str(variant.get("props") or variant.get("scene") or ""),
        },
    }
    return merge_role_intent_generation(
        plan,
        visual_role,
        intent,
        text=text,
        segment_no=segment_no,
        emotion=emotion,
    )


def infer_scene_intent(
    text: str,
    *,
    emotion: str = "",
    segment_no: int = 1,
    total_segments: int = 1,
) -> SceneIntent:
    """根据当前段落文案推断镜头语义（sceneIntent）。"""
    t = (text or "").strip()
    if not t:
        if segment_no <= 1:
            return "opening"
        if segment_no >= max(1, total_segments - 1):
            return "emotion"
        return "opening"

    if _match_any(_COLLAPSE_PATTERNS, t):
        return "collapse"
    if _match_any(_WORK_PRESSURE_PATTERNS, t):
        return "work_pressure"
    if _match_any(_DAILY_LIFE_PATTERNS, t):
        return "daily_life"
    if _match_any(_FATIGUE_PATTERNS, t):
        return "fatigue"

    if _match_any(_OPENING_PATTERNS, t):
        return "opening"
    if _match_any(_COMMUNICATION_PATTERNS, t):
        return "communication"
    if _match_any(_EMOTION_PATTERNS, t):
        return "emotion"

    em = (emotion or "").strip()
    if em in ("疲惫", "累", "tired") and segment_no > total_segments // 2:
        return "fatigue"
    if em in ("紧张", "压力", "stressed", "震惊", "shocked"):
        if re.search(r"上线|还没|催", t):
            return "work_pressure"
        return "work_pressure" if re.search(r"[？?]", t) else "communication"

    if segment_no <= 2:
        return "opening"
    if segment_no >= max(1, total_segments - 1):
        return "emotion"

    return "communication"


def normalize_scene_intent(
    value: Optional[str],
    text: str,
    *,
    emotion: str = "",
    segment_no: int = 1,
    total_segments: int = 1,
) -> SceneIntent:
    raw = (value or "").strip().lower().replace("-", "_")
    if raw in VALID_SCENE_INTENTS:
        return raw  # type: ignore[return-value]
    return infer_scene_intent(
        text,
        emotion=emotion,
        segment_no=segment_no,
        total_segments=total_segments,
    )


def strategy_for_scene_intent(
    intent: SceneIntent,
    text: str = "",
    *,
    emotion: str = "",
    segment_no: int = 1,
    total_segments: int = 1,
    used_scene_keys: Optional[set] = None,
    role_key: str = "",
    career_cn: str = "",
) -> Dict[str, Any]:
    plan = pick_visual_plan(
        intent,
        text,
        emotion=emotion,
        segment_no=segment_no,
        total_segments=total_segments,
        used_scene_keys=used_scene_keys,
        role_key=role_key,
        career_cn=career_cn,
    )
    prefer = list(INTENT_PREFER_TYPES.get(intent, ["scene"]))
    return {
        "sceneIntent": intent,
        "preferTypes": prefer,
        "primaryMaterialType": prefer[0] if prefer else "scene",
        "sceneHints": plan["sceneHints"],
        "sceneKey": plan["sceneKey"],
        "visualPlan": plan,
        "forbidCharacter": intent not in ("emotion",),
    }


def build_intent_tags(
    intent: SceneIntent,
    base_tags: List[str],
    emotion: str,
    *,
    text: str = "",
    segment_no: int = 1,
    role_key: str = "",
    career_cn: str = "",
) -> List[str]:
    from app.ai_short_drama.role_visual_keywords import append_role_visual_tags

    tags = [str(t).strip().lower() for t in base_tags if str(t).strip()]
    strat = strategy_for_scene_intent(
        intent,
        text,
        emotion=emotion,
        segment_no=segment_no,
        role_key=role_key,
        career_cn=career_cn,
    )
    if intent not in tags:
        tags.append(intent)
    for hint in strat["sceneHints"]:
        if hint not in tags:
            tags.append(hint)
    # 剥离易触发工位壁纸的 role 场景 tag
    tags = [t for t in tags if t not in GENERIC_OFFICE_SCENES or t == strat["sceneKey"]]
    if strat["sceneKey"] not in tags:
        tags.append(strat["sceneKey"])
    em = (emotion or "").strip().lower()
    if intent == "work_pressure":
        for ui in ("phone_message", "cold_coffee", "night_office"):
            if ui not in tags:
                tags.append(ui)
    if intent == "collapse":
        for k in ("alert", "terminal", "error_log", "oncall"):
            if k not in tags:
                tags.append(k)
    if em in ("tired", "stressed", "疲惫", "压力") and intent in ("fatigue", "emotion"):
        if "night_office" not in tags:
            tags.append("night_office")
    from app.ai_short_drama.life_moment_visual import (
        life_fragment_tags,
        pick_life_fragment_slugs,
    )

    for slug in life_fragment_tags(
        pick_life_fragment_slugs(intent, text, segment_no=segment_no, count=3)
    ):
        if slug not in tags:
            tags.append(slug)
    if "life_moment" not in tags:
        tags.append("life_moment")
    return append_role_visual_tags(tags, role_key, career_cn)


def _emotion_mood_cn(emotion: str, intent: SceneIntent) -> str:
    em = (emotion or "").strip()
    if intent in ("work_pressure", "collapse"):
        return "压迫内耗、工作侵入生活、非职业介绍"
    if intent in ("fatigue", "emotion"):
        return "疲惫孤独、深夜生活感、电影镜头"
    if intent == "daily_life":
        return "真实生活切片、通勤/雨夜/便利店、非工位展示"
    if em in ("疲惫", "累", "tired", "压抑", "压力", "stressed"):
        return "打工人情绪瞬间"
    return "互联网生活观察、纪录片感"


def build_dynamic_generation_desc(
    text: str,
    intent: SceneIntent,
    emotion: str,
    material_type: str,
    *,
    segment_no: int = 1,
    total_segments: int = 1,
    used_scene_keys: Optional[set] = None,
    role_key: str = "",
    career_cn: str = "",
) -> str:
    """按 sceneIntent + 文案 + 情绪 + 职业视觉关键词生成动态 Prompt。"""
    plan = pick_visual_plan(
        intent,
        text,
        emotion=emotion,
        segment_no=segment_no,
        total_segments=total_segments,
        used_scene_keys=used_scene_keys,
        role_key=role_key,
        career_cn=career_cn,
    )
    gen = plan.get("generation") or {}
    mtype = (material_type or "scene").lower()
    return str(gen.get(mtype) or gen.get("scene") or "")


def generation_desc_for_intent(
    intent: SceneIntent,
    material_type: str,
    *,
    text: str = "",
    emotion: str = "",
    segment_no: int = 1,
    total_segments: int = 1,
) -> str:
    if text:
        return build_dynamic_generation_desc(
            text,
            intent,
            emotion,
            material_type,
            segment_no=segment_no,
            total_segments=total_segments,
        )
    mtype = (material_type or "scene").lower()
    variants = INTENT_VARIANTS.get(intent) or INTENT_VARIANTS["opening"]
    variant = variants[0]
    return str(variant.get(mtype) or variant.get("scene") or "")


def enrich_all_segments(
    segments: List[Dict[str, Any]],
    *,
    career_cn: str = "",
    role_key: str = "",
) -> List[Dict[str, Any]]:
    n = len(segments)
    used_scenes: set = set()
    for seg in segments:
        enrich_segment_with_scene_intent(
            seg,
            total_segments=n,
            used_scene_keys=used_scenes,
            career_cn=career_cn,
            role_key=role_key or str(seg.get("role") or ""),
        )
        sk = str(seg.get("scene") or "")
        if sk:
            used_scenes.add(sk)
    return segments


def enrich_segment_with_scene_intent(
    seg: Dict[str, Any],
    *,
    segment_no: Optional[int] = None,
    total_segments: int = 1,
    used_scene_keys: Optional[set] = None,
    career_cn: str = "",
    role_key: str = "",
) -> Dict[str, Any]:
    text = str(seg.get("text") or "")
    emotion = str(seg.get("emotion") or "")
    seg_no = int(segment_no if segment_no is not None else seg.get("segmentNo") or 1)
    intent = normalize_scene_intent(
        seg.get("sceneIntent") or seg.get("scene_intent"),
        text,
        emotion=emotion,
        segment_no=seg_no,
        total_segments=total_segments,
    )
    seg["sceneIntent"] = intent
    rk = role_key or str(seg.get("role") or "")
    plan = pick_visual_plan(
        intent,
        text,
        emotion=emotion,
        segment_no=seg_no,
        total_segments=total_segments,
        used_scene_keys=used_scene_keys,
        role_key=rk,
        career_cn=career_cn,
    )
    seg["roleVisualKeywords"] = plan.get("visualRole") or ""
    seg["lifeFragments"] = plan.get("lifeFragments") or []
    base_tags = list(seg.get("imageTags") or [])
    seg["imageTags"] = build_intent_tags(
        intent,
        base_tags,
        emotion,
        text=text,
        segment_no=seg_no,
        role_key=rk,
        career_cn=career_cn,
    )
    raw_scene = str(seg.get("scene") or "").strip().lower()
    from app.ai_short_drama.role_visual_keywords import (
        resolve_visual_role_key,
        role_penalized_scenes,
    )

    visual = resolve_visual_role_key(rk, career_cn)
    penalized = role_penalized_scenes(visual)
    if not raw_scene or raw_scene in GENERIC_OFFICE_SCENES or raw_scene in penalized:
        seg["scene"] = plan["sceneKey"]

    from app.ai_short_drama.visual_director import build_scene_description

    primary_mtype = (INTENT_PREFER_TYPES.get(intent) or ["scene"])[0]
    seg["sceneDescription"] = build_scene_description(
        text,
        scene_intent=intent,
        emotion=emotion,
        material_type=primary_mtype,
        segment_no=seg_no,
        total_segments=total_segments,
        llm_scene_description=str(seg.get("sceneDescription") or ""),
        used_scene_keys=used_scene_keys,
        role_key=rk,
        career_cn=career_cn,
    )
    return seg
