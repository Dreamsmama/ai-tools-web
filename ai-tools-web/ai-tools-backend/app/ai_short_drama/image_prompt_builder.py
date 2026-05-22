"""
AI 配图 Prompt 组装：scene_description / 职业视觉 / 生活元素 → 即梦 final_prompt。
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from app.ai_short_drama.life_moment_visual import (
    life_fragments_cn,
    pick_life_fragment_slugs,
)
from app.ai_short_drama.role_visual_keywords import (
    get_role_visual_keywords,
    resolve_visual_role_key,
    role_visual_keywords_cn,
)
from app.ai_short_drama.scene_intent import normalize_scene_intent
from app.ai_short_drama.visual_director import compose_generation_prompt

logger = logging.getLogger(__name__)

VERTICAL_SUFFIX = (
    "9:16竖屏短视频构图，主体居中，上下字幕留白，"
    "中国互联网打工人生活情绪切片，工作侵入生活，"
    "国产互联网动画感半写实，蓝灰深夜色调，电影感瞬间，非职业介绍PPT"
)

FORBIDDEN_PROMPT_BITS = (
    "互联网办公室电脑会议室",
    "程序员在办公室敲代码",
    "工位壁纸",
    "显示器占满画面",
)


@dataclass
class SegmentVisualContext:
    segment_no: int = 1
    text: str = ""
    role_key: str = ""
    career_cn: str = ""
    emotion: str = ""
    scene_intent: str = ""
    scene_description: str = ""
    role_visual_keywords: List[str] = field(default_factory=list)
    life_elements: List[str] = field(default_factory=list)
    visual_prompt: str = ""
    material_type: str = "scene"


def _list_from_segment(item: Any, key: str, alt: str = "") -> List[str]:
    raw = item.get(key) if isinstance(item, dict) else None
    if raw is None and alt:
        raw = item.get(alt) if isinstance(item, dict) else None
    if isinstance(raw, list):
        return [str(x).strip() for x in raw if str(x).strip()]
    if isinstance(raw, str) and raw.strip():
        return [raw.strip()]
    return []


def extract_visual_context_from_segment(
    item: Dict[str, Any],
    *,
    career_cn: str = "",
    total_segments: int = 1,
    material_type: str = "scene",
) -> SegmentVisualContext:
    """从 segment 字典提取视觉上下文（含 lifeFragments / roleVisualKeywords）。"""
    text = str(item.get("text") or "")
    seg_no = int(item.get("segmentNo") or 1)
    role_key = str(item.get("role") or "")
    emotion = str(item.get("emotion") or "")
    intent = normalize_scene_intent(
        item.get("sceneIntent") or item.get("scene_intent"),
        text,
        emotion=emotion,
        segment_no=seg_no,
        total_segments=total_segments,
    )
    visual_role = resolve_visual_role_key(role_key, career_cn)

    scene_desc = str(item.get("sceneDescription") or item.get("scene_description") or "").strip()
    visual_prompt = str(item.get("visualPrompt") or item.get("visual_prompt") or "").strip()

    role_kws = _list_from_segment(item, "roleVisualKeywords", "role_visual_keywords")
    if not role_kws:
        role_kws = get_role_visual_keywords(visual_role)[:6]

    life_slugs = _list_from_segment(item, "lifeFragments", "life_elements")
    if not life_slugs:
        life_slugs = pick_life_fragment_slugs(intent, text, segment_no=seg_no, count=3)
    life_cn = _list_from_segment(item, "lifeElements", "life_elements")
    if not life_cn and life_slugs:
        life_cn = [life_fragments_cn(life_slugs)]
    elif life_cn and life_cn[0] and "_" in life_cn[0] and not any("\u4e00" <= c <= "\u9fff" for c in life_cn[0]):
        life_cn = [life_fragments_cn(life_cn)]

    return SegmentVisualContext(
        segment_no=seg_no,
        text=text,
        role_key=role_key,
        career_cn=career_cn,
        emotion=emotion,
        scene_intent=intent,
        scene_description=scene_desc,
        role_visual_keywords=role_kws,
        life_elements=life_cn,
        visual_prompt=visual_prompt,
        material_type=material_type or "scene",
    )


def build_final_image_prompt(
    ctx: SegmentVisualContext,
    *,
    material_type: Optional[str] = None,
) -> str:
    """
    组合最终即梦 Prompt。优先 scene_description，禁止回退到「办公室+电脑+会议室」。
    """
    mtype = (material_type or ctx.material_type or "scene").lower()
    visual_role = resolve_visual_role_key(ctx.role_key, ctx.career_cn)

    parts: List[str] = []

    # 1. 核心画面（scene_description 最高优先级）
    core = (ctx.scene_description or ctx.visual_prompt or "").strip()
    if core and not any(b in core for b in FORBIDDEN_PROMPT_BITS):
        parts.append(core.rstrip("。.，,"))
    elif ctx.visual_prompt:
        parts.append(ctx.visual_prompt.rstrip("。.，,"))

    # 2. 生活元素（文案 + segment 字段）
    life_slugs = pick_life_fragment_slugs(
        ctx.scene_intent, ctx.text, segment_no=ctx.segment_no, count=3
    )
    life_cn_list = list(ctx.life_elements)
    if not life_cn_list:
        life_cn_list = [life_fragments_cn(life_slugs)]
    life_merged = "，".join(dict.fromkeys(life_cn_list))
    if life_merged:
        parts.append(life_merged)

    # 3. 职业点缀（仅在 sceneDescription 缺失或过短时补充，避免污染已有的生活感描述）
    if len(core) < 20:
        role_cn = role_visual_keywords_cn(visual_role, limit=3)
        if role_cn:
            parts.append(f"职业背景点缀：{role_cn}")

    # 4. 文案氛围（仅在文案含生活场景词时追加，职业叙事文字不注入）
    import re as _re
    _LIFE_TEXT_RE = _re.compile(r"地铁|便利店|咖啡|下班|深夜|凌晨|雨夜|通勤|外卖|孤独|疲惫|加班|城市")
    snippet = (ctx.text or "").strip()[:40]
    if snippet and _LIFE_TEXT_RE.search(snippet):
        parts.append(f"氛围：{snippet}")

    # 5. 情绪
    em = (ctx.emotion or "").strip()
    if em:
        parts.append(f"情绪：{em}")

    if not parts:
        parts.append(build_dynamic_fallback_prompt(ctx))

    body = "，".join(dict.fromkeys(p for p in parts if p))
    final = compose_generation_prompt(body, material_type=mtype)

    log_image_prompt(ctx, final)
    return final


def build_dynamic_fallback_prompt(ctx: SegmentVisualContext) -> str:
    """无 scene_description 时的动态 fallback（禁止写死办公室电脑会议室）。"""
    visual_role = resolve_visual_role_key(ctx.role_key, ctx.career_cn)
    life = life_fragments_cn(
        pick_life_fragment_slugs(ctx.scene_intent, ctx.text, segment_no=ctx.segment_no, count=2)
    )
    role_bit = role_visual_keywords_cn(visual_role, limit=3)
    text_bit = (ctx.text or "")[:32]
    chunks = [c for c in (life, role_bit, text_bit, "疲惫打工人生活瞬间") if c]
    return "，".join(chunks)


def log_image_prompt(ctx: SegmentVisualContext, final_prompt: str) -> None:
    logger.info(
        "[image_prompt] seg=%s text=%s scene_description=%s role=%s "
        "scene_intent=%s role_visual_keywords=%s life_elements=%s final_prompt=%s",
        ctx.segment_no,
        (ctx.text or "")[:48],
        (ctx.scene_description or "")[:120],
        ctx.role_key,
        ctx.scene_intent,
        ",".join(ctx.role_visual_keywords[:6]),
        ",".join(ctx.life_elements[:6]),
        final_prompt[:500],
    )
