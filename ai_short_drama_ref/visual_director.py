"""
职业观察局 · 视觉导演层。

根据文案语义动态生成 sceneDescription / 生图 Prompt，
统一「中国互联网职场宇宙」画风：生活情绪切片，非职业科普 PPT。
"""

from __future__ import annotations

from typing import Optional

from app.ai_short_drama.scene_intent import (
    SceneIntent,
    build_dynamic_generation_desc,
    normalize_scene_intent,
)

# ── 世界观（写入 LLM system / 生图后缀）────────────────────────────

VISUAL_DIRECTOR_SYSTEM = """你是《职业观察局》短视频的视觉导演。

【定位】不是职业科普，是「互联网人的生活情绪」短视频（打工人深夜观察 / 生活切片）。
职业只是入口；真正打动人的是：疲惫、深夜、孤独、内耗、工作侵入生活。

【任务】为每段文案设计 9:16 竖屏画面，像电影镜头瞬间，不像职业介绍 PPT。

【画风】国产互联网动画感、半写实插画、蓝灰冷色调、年轻打工人、情绪感、深夜感。

【构图】竖屏，主体居中，上下字幕留白，适合抖音/小红书。

【必须】每段至少 2 项「生活碎片」：冷咖啡、深夜便利店、地铁、雨夜窗边、凌晨办公室、耳机、外卖、城市夜景、手机消息、下班电梯等。
【职业元素】可出现，但只占画面一部分（虚化/一角/背景），禁止软件界面占满全屏。

【禁止】
- 职业科普句式（如「程序员在办公室敲代码」）
- 全片工位/会议室/电脑壁纸
- 科幻、赛博朋克、游戏 CG

【正确镜头示例】
「凌晨互联网办公室，冷掉的咖啡，亮着的显示器，窗外城市夜景，疲惫安静，竖屏留白。」"""

VISUAL_STYLE_SUFFIX = (
    "中国互联网打工人生活情绪，工作侵入生活，国产互联网动画感半写实，"
    "蓝灰深夜色调，电影感竖屏瞬间，9:16抖音小红书，上下字幕留白，非职业介绍PPT"
)

VISUAL_FORBIDDEN_SUFFIX = (
    "禁止：职业科普口吻、办公室敲代码、软件界面占满画面、工位壁纸、科幻赛博朋克"
)

GENERIC_TEMPLATE_MARKERS = (
    "会议室",
    "工位",
    "显示器",
    "办公桌",
    "电脑",
    "办公室一角",
    "在办公室",
    "敲代码",
)


def is_generic_scene_description(desc: str) -> bool:
    """判断是否为「会议室+电脑」或职业 PPT 类空泛描述。"""
    from app.ai_short_drama.life_moment_visual import is_career_ppt_description

    t = (desc or "").strip()
    if len(t) < 8:
        return True
    if is_career_ppt_description(t):
        return True
    hits = sum(1 for m in GENERIC_TEMPLATE_MARKERS if m in t)
    return hits >= 2 and len(t) < 45


def compose_generation_prompt(
    scene_description: str,
    *,
    material_type: str = "scene",
) -> str:
    """将 sceneDescription 包装为即梦可用的完整风格约束。"""
    core = (scene_description or "").strip().rstrip("。.，,")
    mtype = (material_type or "scene").lower()
    if not core:
        core = "深夜城市与办公光影交织，冷咖啡与手机微光，情绪留白"
    parts = [core, VISUAL_STYLE_SUFFIX, VISUAL_FORBIDDEN_SUFFIX]
    if mtype == "ui":
        parts.insert(1, "竖屏手机消息或界面一角，融入生活场景，非纯软件PPT截图")
    elif mtype == "effects":
        parts.insert(1, "竖屏雨夜/夜景/灯光氛围，轻量情绪特效")
    elif mtype == "props":
        parts.insert(1, "竖屏生活道具特写：咖啡/耳机/外卖，浅景深")
    else:
        parts.insert(1, "竖屏生活感场景空镜或中景，电影瞬间，非工位壁纸")
    return "，".join(p for p in parts if p)


def build_scene_description(
    text: str,
    *,
    scene_intent: Optional[str] = None,
    emotion: str = "",
    material_type: str = "scene",
    segment_no: int = 1,
    total_segments: int = 1,
    llm_scene_description: str = "",
    used_scene_keys: Optional[set] = None,
    role_key: str = "",
    career_cn: str = "",
) -> str:
    """
    生成单段 sceneDescription（视觉导演主入口）。

    优先 LLM 描述（若符合生活瞬间）；否则规则生成电影感镜头。
    """
    from app.ai_short_drama.life_moment_visual import (
        compose_cinematic_moment,
        is_career_ppt_description,
    )
    from app.ai_short_drama.role_visual_keywords import (
        is_generic_scene_for_role,
        resolve_visual_role_key,
    )

    intent: SceneIntent = normalize_scene_intent(
        scene_intent,
        text,
        emotion=emotion,
        segment_no=segment_no,
        total_segments=total_segments,
    )
    visual = resolve_visual_role_key(role_key, career_cn)
    llm_desc = (llm_scene_description or "").strip()
    if (
        llm_desc
        and not is_generic_scene_for_role(llm_desc, role_key=role_key, career_cn=career_cn)
        and not is_career_ppt_description(llm_desc)
    ):
        return compose_cinematic_moment(
            llm_desc,
            visual_role=visual,
            intent=intent,
            text=text,
            segment_no=segment_no,
            emotion=emotion,
        )

    return build_dynamic_generation_desc(
        text,
        intent,
        emotion,
        material_type,
        segment_no=segment_no,
        total_segments=total_segments,
        used_scene_keys=used_scene_keys,
        role_key=role_key,
        career_cn=career_cn,
    )
