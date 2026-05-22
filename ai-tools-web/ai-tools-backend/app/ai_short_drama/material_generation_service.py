from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.ai_short_drama.image_prompt_builder import (
    SegmentVisualContext,
    build_final_image_prompt,
    extract_visual_context_from_segment,
)
from app.ai_short_drama.jimeng_image_provider import (
    ImageGenerationError,
    generate_dynamic_image,
)
from app.ai_short_drama.material_cache import (
    build_cache_key,
    find_cached_dynamic_material,
    normalize_style,
)
from app.ai_short_drama.material_image_validate import (
    ImageValidationError,
    normalize_material_image_bytes,
    validate_image_path,
)
from app.ai_short_drama.vertical_image import VERTICAL_SIZE_API
from app.ai_short_drama.material_infer import infer_emotion_key, normalize_tags
from app.ai_short_drama.material_paths import (
    UPLOAD_ROOT,
    build_ai_dynamic_paths,
    url_to_disk_path,
)
from app.ai_short_drama.material_asset_filter import is_placeholder_material_record
from app.ai_short_drama.material_store import material_store
from app.ai_short_drama.tag_utils import ensure_material_tags

logger = logging.getLogger(__name__)

FORBIDDEN_AI_TYPES = frozenset({"character"})


def build_generation_prompt(
    *,
    material_type: str,
    scene: str,
    emotion: str,
    scene_text: str,
    emotion_text: str,
    tags: List[str],
    props: List[str],
    scene_intent: str = "",
    segment_text: str = "",
    segment_no: int = 1,
    total_segments: int = 1,
    scene_description: str = "",
    role_key: str = "",
    career_cn: str = "",
    role_visual_keywords: Optional[List[str]] = None,
    life_elements: Optional[List[str]] = None,
    visual_prompt: str = "",
) -> str:
    """组装最终 AI 配图 Prompt（优先 scene_description）。"""
    item: Dict[str, Any] = {
        "segmentNo": segment_no,
        "text": segment_text,
        "role": role_key,
        "emotion": emotion_text or emotion,
        "sceneIntent": scene_intent,
        "sceneDescription": scene_description,
        "roleVisualKeywords": role_visual_keywords or [],
        "lifeElements": life_elements or [],
        "visualPrompt": visual_prompt,
    }
    ctx = extract_visual_context_from_segment(
        item,
        career_cn=career_cn,
        total_segments=total_segments,
        material_type=material_type,
    )
    return build_final_image_prompt(ctx, material_type=material_type)


def _material_display_name(material_type: str, scene_key: str, emotion_key: str, tags: List[str]) -> str:
    if material_type == "ui":
        return f"UI素材-{(tags[0] if tags else '界面')}"
    if material_type == "props":
        return f"道具-{(tags[0] if tags else '道具')}"
    if scene_key and scene_key not in ("office", "desk", "meeting_room"):
        return f"场景-{scene_key}"
    return f"生活感素材-{(tags[0] if tags else '瞬间')}"


def _validate_cached_record(cached: Dict[str, Any]) -> bool:
    if is_placeholder_material_record(cached):
        return False
    url = cached.get("url") or ""
    path = url_to_disk_path(url)
    if not path:
        return False
    try:
        mtype = str(cached.get("type") or "scene")
        validate_image_path(path, material_type=mtype)
        return True
    except ImageValidationError as err:
        logger.warning("[素材缓存] 缓存无效将忽略: %s — %s", url, err)
        return False


async def generate_and_cache_dynamic_material(
    *,
    image_tags: List[str],
    scene: str = "",
    emotion: str = "",
    scene_text: str = "",
    emotion_text: str = "",
    props: Optional[List[str]] = None,
    style: str = "",
    material_type: Optional[str] = None,
    scene_intent: str = "",
    segment_text: str = "",
    segment_no: int = 1,
    total_segments: int = 1,
    scene_description: str = "",
    role_key: str = "",
    career_cn: str = "",
    role_visual_keywords: Optional[List[str]] = None,
    life_elements: Optional[List[str]] = None,
    visual_prompt: str = "",
) -> Dict[str, Any]:
    """
    生成 scene/ui/props/effects 素材；Prompt 由 scene_description + 职业/生活元素组合。
    """
    tags = normalize_tags(image_tags)
    props_list = [str(p).strip().lower() for p in (props or []) if str(p).strip()]
    for p in props_list:
        if p not in tags:
            tags.append(p)

    mtype = material_type or "scene"
    if mtype in FORBIDDEN_AI_TYPES:
        raise ImageGenerationError("禁止 AI 自动生成职业人物素材")

    ctx = SegmentVisualContext(
        segment_no=segment_no,
        text=segment_text,
        role_key=role_key,
        career_cn=career_cn,
        emotion=emotion_text or emotion,
        scene_intent=scene_intent,
        scene_description=scene_description,
        role_visual_keywords=list(role_visual_keywords or []),
        life_elements=list(life_elements or []),
        visual_prompt=visual_prompt,
        material_type=mtype,
    )
    if not ctx.scene_description and segment_text:
        ctx = extract_visual_context_from_segment(
            {
                "segmentNo": segment_no,
                "text": segment_text,
                "role": role_key,
                "emotion": ctx.emotion,
                "sceneIntent": scene_intent,
                "sceneDescription": scene_description,
                "roleVisualKeywords": role_visual_keywords or [],
                "lifeElements": life_elements or [],
                "visualPrompt": visual_prompt,
            },
            career_cn=career_cn,
            total_segments=total_segments,
            material_type=mtype,
        )

    # 缓存键仍用 tag/scene，但生成不以 office/desk 为主导
    scene_key = "life_moment"
    if tags:
        scene_key = tags[0]
    emotion_key = infer_emotion_key(emotion_text or emotion)
    style_key = normalize_style(style)

    cached = find_cached_dynamic_material(
        material_type=mtype,
        scene=scene_key,
        emotion=emotion_key,
        style=style_key,
        tags=tags,
    )
    if cached and _validate_cached_record(cached):
        logger.info(
            "[素材缓存] 缓存命中 scene=%s type=%s url=%s",
            scene_key,
            mtype,
            cached.get("url"),
        )
        return {
            "id": cached["id"],
            "name": cached["name"],
            "url": cached["url"],
            "tags": list(cached.get("tags") or []),
            "aiGenerated": True,
            "cacheHit": True,
            "source": "cache",
        }

    prompt = build_final_image_prompt(ctx, material_type=mtype)

    logger.info(
        "[AI生成] 开始 type=%s seg=%s intent=%s",
        mtype,
        segment_no,
        ctx.scene_intent,
    )

    try:
        gen = await generate_dynamic_image(prompt, size=VERTICAL_SIZE_API)
    except ImageGenerationError:
        raise
    except Exception as err:
        logger.exception("[AI生成] 异常 seg=%s", segment_no)
        raise ImageGenerationError(f"即梦图片生成失败：{err}") from err

    try:
        png_bytes, orient = normalize_material_image_bytes(gen.data, material_type=mtype)
        logger.info(
            "[AI生成] 竖屏校验通过 %sx%s ratio=%s",
            orient.width,
            orient.height,
            orient.aspect_ratio,
        )
    except ImageValidationError as err:
        raise ImageGenerationError(f"图片校验失败：{err}") from err

    paths = build_ai_dynamic_paths(
        material_type=mtype,
        scene=scene_key,
        emotion=emotion_key,
        tags=tags,
        props=props_list,
    )

    dest = UPLOAD_ROOT / paths["rel_path"]
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(png_bytes)

    logger.info(
        "[AI生成] provider=%s 成功 image_url=%s path=%s",
        gen.provider,
        (gen.image_url or "")[:120],
        paths["rel_path"],
    )

    image_meta = orient.to_meta_dict()
    cache_key = build_cache_key(
        material_type=mtype,
        scene=scene_key,
        emotion=emotion_key,
        style=style_key,
        tags=tags,
    )

    name = _material_display_name(mtype, scene_key, emotion_key, tags)
    payload = {
        "id": paths["id"],
        "name": name,
        "type": mtype,
        "role": role_key or "none",
        "emotion": emotion_key,
        "scene": scene_key,
        "url": paths["url"],
        "tags": ensure_material_tags(
            {"type": mtype, "role": role_key or "none", "emotion": emotion_key, "scene": scene_key},
            tags + ["ai_generated", style_key, "life_moment"],
        ),
        "aiGenerated": True,
        "isPlaceholder": False,
        "style": style_key,
        "cacheKey": cache_key,
        **image_meta,
    }

    generated_row = {
        "id": paths["id"],
        "name": name,
        "url": paths["url"],
        "tags": payload["tags"],
        "type": mtype,
        "aiGenerated": True,
        "cacheHit": False,
        "source": "generated",
        "sceneDescription": ctx.scene_description,
        **image_meta,
    }

    try:
        row = material_store.create_material(payload)
    except Exception as err:
        logger.exception("persist generated material failed: %s", err)
        return generated_row

    if not row or not isinstance(row, dict):
        return generated_row

    return {
        "id": row.get("id") or paths["id"],
        "name": row.get("name") or name,
        "url": row.get("url") or paths["url"],
        "tags": list(row.get("tags") or payload["tags"]),
        "type": row.get("type") or mtype,
        "aiGenerated": True,
        "cacheHit": False,
        "source": "generated",
        "sceneDescription": ctx.scene_description,
        **image_meta,
    }
