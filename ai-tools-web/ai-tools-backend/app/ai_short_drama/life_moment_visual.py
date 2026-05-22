"""
生活感视觉层：职业观察局 = 互联网人的生活情绪切片，不是职业科普 PPT。

职业元素只占画面一部分；自动叠加生活碎片（咖啡、地铁、雨夜等）。
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from app.ai_short_drama.scene_intent import SceneIntent

# 生活碎片（中文展示 + 英文 tag）
LIFE_FRAGMENTS: List[Tuple[str, str]] = [
    ("冷掉的咖啡", "cold_coffee"),
    ("深夜便利店", "convenience_store"),
    ("夜晚地铁", "subway_night"),
    ("下班电梯", "elevator"),
    ("雨夜窗边", "rainy_window"),
    ("凌晨办公室", "night_office"),
    ("耳机", "headphones"),
    ("外卖盒", "takeout"),
    ("凌乱桌面", "messy_desk"),
    ("城市夜景", "city_night"),
    ("路灯", "street_lamp"),
    ("空会议室", "empty_meeting"),
    ("下班后的工位", "after_hours_desk"),
    ("凌晨城市", "dawn_city"),
    ("手机消息", "phone_message"),
    ("夜晚灯光", "night_light"),
    ("通勤背影", "commute"),
    ("便利店暖光", "store_light"),
    ("空荡走廊", "corridor"),
    ("窗边剪影", "window_silhouette"),
]

# 按 sceneIntent 优先抽取的生活池
INTENT_LIFE_POOLS: Dict[str, List[str]] = {
    "opening": ["city_night", "commute", "elevator", "convenience_store", "street_lamp"],
    "communication": ["phone_message", "elevator", "headphones", "night_light"],
    "work_pressure": ["cold_coffee", "phone_message", "night_office", "messy_desk", "takeout"],
    "fatigue": ["cold_coffee", "after_hours_desk", "night_office", "headphones", "rainy_window"],
    "collapse": ["night_office", "city_night", "phone_message", "messy_desk"],
    "emotion": ["rainy_window", "city_night", "window_silhouette", "dawn_city", "commute"],
    "daily_life": ["subway_night", "convenience_store", "takeout", "commute", "rainy_window"],
}

# 文案触发的额外生活碎片
_TEXT_LIFE_HINTS: List[Tuple[str, str]] = [
    (r"地铁|通勤|公交", "subway_night"),
    (r"咖啡", "cold_coffee"),
    (r"雨|窗外", "rainy_window"),
    (r"深夜|凌晨|晚上", "night_office"),
    (r"外卖", "takeout"),
    (r"消息|飞书|微信", "phone_message"),
    (r"下班|回家", "commute"),
    (r"便利店", "convenience_store"),
    (r"电梯", "elevator"),
    (r"孤独|累|疲惫", "window_silhouette"),
    (r"空办公室|空荡", "empty_meeting"),
    (r"城市夜景|夜景", "city_night"),
    (r"冷掉|冷咖啡", "cold_coffee"),
]

# 职业 PPT / 科普口吻（需重写）
PPT_STYLE_MARKERS: tuple[str, ...] = (
    "在办公室",
    "敲代码",
    "介绍",
    "展示",
    "工作场景",
    "职业",
    "岗位",
    "主要负责",
    "日常工作",
    "使用电脑",
    "对着电脑",
    "软件界面占满",
)

# 每职业：镜头里「点缀」用的职业符号（1 个即可，勿占满画幅）
ROLE_MOMENT_ACCENT: Dict[str, List[str]] = {
    "programmer": ["显示器一角VSCode虚化", "终端窗口小景", "键盘旁日志"],
    "designer": ["MacBook暖光", "色卡与草图", "改稿到凌晨的屏幕一角"],
    "product_manager": ["手机飞书消息", "白板便利贴一角", "电梯里回消息"],
    "hr": ["简历文件夹", "微信邀约", "面试间空椅"],
    "operations": ["数据屏一角", "活动页草稿", "社群消息红点"],
    "tester": ["Bug列表一角", "测试机"],
    "devops": ["监控屏红光", "终端告警"],
    "sales": ["微信客户", "深夜电话"],
}

_SLUG_TO_CN: Dict[str, str] = {slug: cn for cn, slug in LIFE_FRAGMENTS}


def _variant_index(seed: str, modulo: int) -> int:
    if modulo <= 0:
        return 0
    return sum(ord(c) for c in seed) % 9973 % modulo


def pick_life_fragment_slugs(
    intent: str,
    text: str = "",
    *,
    segment_no: int = 1,
    count: int = 2,
) -> List[str]:
    """为本段挑选 2~3 个生活碎片 tag。"""
    pool = list(INTENT_LIFE_POOLS.get(intent) or INTENT_LIFE_POOLS["emotion"])
    t = (text or "").strip()
    for pattern, slug in _TEXT_LIFE_HINTS:
        if re.search(pattern, t) and slug not in pool:
            pool.insert(0, slug)
    seed = f"{segment_no}:{intent}:{t[:32]}"
    idx = _variant_index(seed, len(pool))
    picked: List[str] = []
    for offset in range(len(pool)):
        slug = pool[(idx + offset) % len(pool)]
        if slug not in picked:
            picked.append(slug)
        if len(picked) >= count:
            break
    return picked


def life_fragments_cn(slugs: List[str]) -> str:
    parts = [_SLUG_TO_CN.get(s, s) for s in slugs if s]
    return "，".join(parts)


def life_fragment_tags(slugs: List[str]) -> List[str]:
    return [s for s in slugs if s]


def pick_role_accent(visual_role: str, segment_no: int = 1) -> str:
    accents = ROLE_MOMENT_ACCENT.get(visual_role) or ROLE_MOMENT_ACCENT["programmer"]
    if not accents:
        return ""
    return accents[_variant_index(str(segment_no), len(accents))]


def is_career_ppt_description(desc: str) -> bool:
    """是否像职业介绍 PPT，而非生活瞬间。"""
    t = (desc or "").strip()
    if len(t) < 10:
        return True
    ppt_hits = sum(1 for m in PPT_STYLE_MARKERS if m in t)
    life_hits = sum(1 for cn, _ in LIFE_FRAGMENTS if cn in t)
    work_only = sum(1 for w in ("会议室", "工位", "PPT", "PRD", "Figma界面", "软件") if w in t)
    if ppt_hits >= 1:
        return True
    if work_only >= 2 and life_hits == 0 and len(t) < 50:
        return True
    return False


def compose_cinematic_moment(
    base: str,
    *,
    visual_role: str,
    intent: str,
    text: str = "",
    segment_no: int = 1,
    emotion: str = "",
) -> str:
    """
    电影感瞬间描述：生活碎片 + 职业点缀 + 情绪，禁止职业科普口吻。
    """
    life_slugs = pick_life_fragment_slugs(intent, text, segment_no=segment_no, count=2)
    life_cn = life_fragments_cn(life_slugs)
    accent = pick_role_accent(visual_role, segment_no)
    mood = _moment_mood(intent, emotion)

    core = (base or "").strip().rstrip("。.，,")
    # 若 base 已是纯软件/会议室描述，弱化保留
    if is_career_ppt_description(core):
        core = ""

    parts: List[str] = []
    if life_cn:
        parts.append(life_cn)
    if accent and accent not in (core or ""):
        parts.append(accent)
    if core and not is_career_ppt_description(core):
        parts.append(core)
    if mood:
        parts.append(mood)
    snippet = (text or "").strip()[:28]
    if snippet and "文案" not in "".join(parts):
        parts.append(f"瞬间氛围：{snippet}")

    snippet = (text or "").strip()[:28]
    if snippet and "文案" not in "".join(parts):
        parts.append(f"瞬间氛围：{snippet}")

    deduped: List[str] = []
    seen: set = set()
    for p in parts:
        key = p[:24]
        if p and key not in seen:
            seen.add(key)
            deduped.append(p)
    shot = "，".join(deduped)
    if not shot:
        shot = f"{life_cn}，{accent}，互联网打工人情绪留白" if life_cn else "深夜城市与办公光影交织的生活瞬间"
    return shot


def _moment_mood(intent: str, emotion: str) -> str:
    em = (emotion or "").strip()
    if intent in ("fatigue", "emotion"):
        return "疲惫孤独、工作侵入生活、电影感竖屏瞬间"
    if intent == "daily_life":
        return "真实生活切片、纪实感、非工作展示"
    if intent in ("work_pressure", "collapse"):
        return "压迫内耗、深夜互联网氛围"
    if intent == "opening":
        return "留白、情绪铺垫、非职业介绍"
    if em in ("疲惫", "累", "压抑", "压力"):
        return "打工人真实情绪"
    return "国产互联网动画感生活瞬间"


def blend_life_into_plan(
    plan: Dict[str, Any],
    visual_role: str,
    intent: str,
    text: str = "",
    *,
    segment_no: int = 1,
    emotion: str = "",
) -> Dict[str, Any]:
    """将 visual plan 的 generation 转为生活感电影镜头，并追加 life tags。"""
    gen = dict(plan.get("generation") or {})
    life_slugs = pick_life_fragment_slugs(intent, text, segment_no=segment_no, count=3)

    for mtype in ("scene", "ui", "effects", "props"):
        raw = str(gen.get(mtype) or gen.get("scene") or "")
        if mtype == "ui":
            # UI 镜头也加生活语境，避免纯软件 PPT
            gen[mtype] = compose_cinematic_moment(
                raw if raw else "手机屏幕消息特写",
                visual_role=visual_role,
                intent=intent,
                text=text,
                segment_no=segment_no,
                emotion=emotion,
            )
        elif raw or mtype == "scene":
            gen[mtype] = compose_cinematic_moment(
                raw,
                visual_role=visual_role,
                intent=intent,
                text=text,
                segment_no=segment_no,
                emotion=emotion,
            )

    plan["generation"] = gen
    hints = list(plan.get("sceneHints") or [])
    for slug in life_fragment_tags(life_slugs):
        if slug not in hints:
            hints.append(slug)
    hints.append("life_moment")
    plan["sceneHints"] = hints
    plan["lifeFragments"] = life_slugs

    # 情绪/生活类 intent 优先夜景场景 key
    if intent in ("fatigue", "emotion", "daily_life", "collapse"):
        sk = str(plan.get("sceneKey") or "")
        if sk in ("desk", "meeting_room", "workstation", "office_day"):
            plan["sceneKey"] = "night_office" if intent != "daily_life" else "office_night"

    return plan


def prompt_life_moment_block() -> str:
    """LLM：生活感 + 电影镜头写法。"""
    samples = "、".join(cn for cn, _ in LIFE_FRAGMENTS[:10])
    return f"""
【生活感 · 视觉原则】职业观察局不是职业科普，是「互联网人的生活情绪」。
- 职业只是入口；画面核心是：疲惫、深夜、孤独、内耗、工作侵入生活。
- 每段 sceneDescription 须像电影镜头（40-90字），禁止「XX在办公室做YY」的职业介绍句式。
- 每段至少包含 2 项生活碎片（如：{samples}…），职业符号只占画面一部分（虚化/一角/背景）。
- 错误示例：「程序员在办公室敲代码。」
- 正确示例：「凌晨互联网办公室，冷掉的咖啡，亮着的显示器，窗外城市夜景，疲惫安静，竖屏留白。」
"""
