from __future__ import annotations

import logging
import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

from app.ai_short_drama.character_ip_store import character_ip_store
from app.ai_short_drama.jimeng_image_provider import AI_IMAGE_FAILED_MSG, ImageGenerationError
from app.ai_short_drama.material_asset_filter import filter_matchable_materials
from app.ai_short_drama.material_generation_service import generate_and_cache_dynamic_material
from app.ai_short_drama.material_image_validate import ImageValidationError, validate_image_path
from app.ai_short_drama.material_infer import (
    ROLE_CN_TO_KEY,
    infer_emotion_key,
    infer_role_key,
    normalize_scene_key,
    normalize_tags,
    scene_match_keys,
)
from app.ai_short_drama.material_paths import url_to_disk_path
from app.ai_short_drama.material_store import material_store
from app.ai_short_drama.scene_intent import infer_scene_intent, normalize_scene_intent
from app.ai_short_drama.segment_material_strategy import (
    build_segment_tags,
    classify_segment_content,
    merged_material_strategy,
)
from app.ai_short_drama.video_material_plan import slot_to_prefer_types

logger = logging.getLogger(__name__)

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
FRONTEND_PUBLIC = BACKEND_ROOT.parent / "ai-tools-frontend" / "public"

LIBRARY_MIN_SCORE = 2
USED_ID_PENALTY = 10_000
REPEAT_TYPE_PENALTY = 8
REPEAT_URL_PENALTY = 12_000

AI_GENERATABLE_TYPES = frozenset({"scene", "ui", "props", "effects"})

_CATALOG_CACHE: List[Dict[str, Any]] | None = None
_CATALOG_CACHE_AT: float = 0.0
_CATALOG_CACHE_TTL = 45.0

MISSING_MATERIAL_MSG = "缺少可用素材，请上传人物图或生成真实场景图"
CHARACTER_IP_MISSING_MSG = "请先在角色IP管理中配置并确认基础角色"


def _url_exists(url: str) -> bool:
    if not url or not str(url).strip():
        return False
    raw = str(url).strip()
    if raw.startswith("/uploads/"):
        path = url_to_disk_path(raw)
        return path is not None and path.is_file()
    if raw.startswith("/short-drama/"):
        rel = raw[len("/short-drama/") :]
        return (FRONTEND_PUBLIC / "short-drama" / rel).is_file()
    return False


@lru_cache(maxsize=512)
def _is_valid_library_file_cached(url: str, material_type: str) -> bool:
    from app.ai_short_drama.material_asset_filter import is_placeholder_material_record

    if is_placeholder_material_record({"url": url}):
        return False
    path = url_to_disk_path(url) if url.startswith("/uploads/") else None
    if path and path.is_file():
        try:
            validate_image_path(path, material_type=material_type)
            return True
        except ImageValidationError:
            return False
    return False


def _is_valid_library_file(url: str, *, material_type: str = "scene") -> bool:
    return _is_valid_library_file_cached(url, (material_type or "scene").lower())


def invalidate_material_validation_cache() -> None:
    _is_valid_library_file_cached.cache_clear()


def _is_library_item(item: Dict[str, Any]) -> bool:
    from app.ai_short_drama.material_asset_filter import is_placeholder_material_record

    if is_placeholder_material_record(item):
        return False
    url = (item.get("url") or "").strip()
    if not url:
        return False
    if url.startswith("/short-drama/"):
        return _url_exists(url)
    if url.startswith("/uploads/") or bool(item.get("aiGenerated")):
        return _is_valid_library_file(url, material_type=str(item.get("type") or "scene"))
    return False


def _load_catalog(*, force_refresh: bool = False) -> List[Dict[str, Any]]:
    global _CATALOG_CACHE, _CATALOG_CACHE_AT
    now = time.monotonic()
    if (
        not force_refresh
        and _CATALOG_CACHE is not None
        and (now - _CATALOG_CACHE_AT) < _CATALOG_CACHE_TTL
    ):
        return _CATALOG_CACHE
    try:
        db_items = material_store.list_materials()
    except Exception as err:
        logger.warning("load db materials failed: %s", err)
        db_items = []
    _CATALOG_CACHE = filter_matchable_materials(db_items)
    _CATALOG_CACHE_AT = now
    return _CATALOG_CACHE


def preload_match_catalog() -> int:
    """预加载素材库（整次 /generate 前调用一次）。"""
    return len(_load_catalog(force_refresh=True))


def _scene_keys_match(item_scene: str, target_scene: str) -> bool:
    if not item_scene or item_scene == "none":
        return False
    return bool(set(scene_match_keys(item_scene)) & set(scene_match_keys(target_scene)))


def _score_material(
    item: Dict[str, Any],
    tag_set: set,
    role_key: str,
    emotion_key: str,
    scene_key: str,
    *,
    prefer_types: Optional[List[str]] = None,
    career_cn: str = "",
) -> int:
    from app.ai_short_drama.role_visual_keywords import (
        resolve_visual_role_key,
        role_penalized_scenes,
        role_visual_tag_slugs,
    )

    item_tags = set(normalize_tags(item.get("tags") or []))
    score = len(tag_set & item_tags) * 2

    visual = resolve_visual_role_key(role_key, career_cn)
    for slug in role_visual_tag_slugs(visual):
        if slug in tag_set and slug in item_tags:
            score += 4

    if "life_moment" in tag_set:
        if "life_moment" in item_tags:
            score += 3
        from app.ai_short_drama.life_moment_visual import _SLUG_TO_CN

        for slug in tag_set:
            if slug in _SLUG_TO_CN and slug in item_tags:
                score += 5

    item_role = (item.get("role") or "none").lower()
    if role_key != "none" and item_role == role_key:
        score += 3

    item_emotion = (item.get("emotion") or "none").lower()
    if emotion_key != "none" and item_emotion == emotion_key:
        score += 2

    item_scene = (item.get("scene") or "none").lower()
    if scene_key != "none" and _scene_keys_match(item_scene, scene_key):
        score += 4

    penalized = role_penalized_scenes(visual)
    if item_scene in penalized or any(
        sk in penalized for sk in scene_match_keys(item_scene)
    ):
        score -= 10

    mtype = (item.get("type") or "scene").lower()
    if prefer_types and mtype in prefer_types:
        score += 6 - prefer_types.index(mtype) * 2

    return score


def _pick_best_candidate(
    catalog: List[Dict[str, Any]],
    tag_set: set,
    role_key: str,
    emotion_key: str,
    scene_key: str,
    *,
    prefer_types: List[str],
    forbid_character: bool = False,
    used_material_ids: Optional[Set[str]] = None,
    used_material_urls: Optional[Set[str]] = None,
    recent_types: Optional[List[str]] = None,
    career_cn: str = "",
) -> Tuple[Optional[Dict[str, Any]], int]:
    """在候选中选得分最高且尽量避免重复的镜头。"""
    used_ids = used_material_ids or set()
    used_urls = used_material_urls or set()
    recent = list(recent_types or [])[-2:]

    ranked: List[Tuple[int, Dict[str, Any]]] = []

    for item in catalog:
        if not _is_library_item(item):
            continue
        mtype = (item.get("type") or "scene").lower()
        # 人物镜头仅走角色 IP，不从普通素材库抽人物图
        if mtype == "character":
            continue
        if prefer_types and mtype not in prefer_types:
            continue

        score = _score_material(
            item,
            tag_set,
            role_key,
            emotion_key,
            scene_key,
            prefer_types=prefer_types,
            career_cn=career_cn,
        )
        if score < 1:
            continue

        mid = str(item.get("id") or "")
        url = (item.get("url") or "").strip()
        if mid and mid in used_ids:
            score -= USED_ID_PENALTY
        if url and url in used_urls:
            score -= REPEAT_URL_PENALTY
        if recent.count(mtype) >= 2:
            score -= REPEAT_TYPE_PENALTY
        elif recent and recent[-1] == mtype:
            score -= REPEAT_TYPE_PENALTY // 2

        ranked.append((score, item))

    if not ranked:
        return None, 0

    ranked.sort(key=lambda x: x[0], reverse=True)
    best_score, best = ranked[0]
    if best_score < -1000:
        # 全部因重复被压分，取原最高分换一张不同的
        for score, item in ranked:
            mid = str(item.get("id") or "")
            url = (item.get("url") or "").strip()
            if mid not in used_ids and url not in used_urls:
                return item, score
        return ranked[0][1], ranked[0][0]

    return best, best_score


def _material_from_character_ip(ip: Dict[str, Any], *, content_type: str) -> Dict[str, Any]:
    url = (ip.get("baseImageUrl") or "").strip()
    if not url or not _is_valid_library_file(url):
        return _missing_material(error=CHARACTER_IP_MISSING_MSG, content_type=content_type)
    return {
        "id": ip.get("id") or "character_ip",
        "name": ip.get("name") or "角色IP",
        "url": url,
        "tags": ["character_ip", "character", ip.get("role") or ""],
        "aiGenerated": ip.get("source") == "ai_generated",
        "cacheHit": False,
        "source": "character_ip",
        "materialStatus": "ready",
        "materialError": None,
        "materialType": "character",
        "contentType": content_type,
    }


def _resolve_character_ip_for_role(role_key: str) -> Optional[Dict[str, Any]]:
    if not role_key or role_key == "none":
        return None
    return character_ip_store.get_active(role_key)


def _material_result(
    item: Optional[Dict[str, Any]],
    *,
    source: str = "catalog",
    cache_hit: bool = False,
    material_type: str = "scene",
    content_type: str = "monologue",
) -> Dict[str, Any]:
    if not item:
        return _missing_material(content_type=content_type)
    url = (item.get("url") or "").strip()
    mtype = (item.get("type") or material_type or "scene").lower()
    if mtype == "effects":
        mtype = "effect"
    if not url or not _is_valid_library_file(url, material_type=mtype):
        return _missing_material(content_type=content_type)
    out: Dict[str, Any] = {
        "id": item["id"],
        "name": item.get("name", ""),
        "url": url,
        "tags": list(item.get("tags") or []),
        "aiGenerated": bool(item.get("aiGenerated")),
        "cacheHit": cache_hit,
        "source": source,
        "materialStatus": "ready",
        "materialError": None,
        "materialType": mtype,
        "contentType": content_type,
    }
    for key in ("imageWidth", "imageHeight", "aspectRatio", "isVertical", "exifOrientation"):
        if key in item:
            out[key] = item[key]
    return out


def _missing_material(*, error: Optional[str] = None, content_type: str = "monologue") -> Dict[str, Any]:
    msg = (error or "").strip() or MISSING_MATERIAL_MSG
    return {
        "id": "material_missing",
        "name": msg,
        "url": "",
        "tags": [],
        "aiGenerated": False,
        "cacheHit": False,
        "source": "missing",
        "materialStatus": "missing",
        "materialError": msg,
        "materialType": "",
        "contentType": content_type,
    }


async def _try_ai_generate(
    *,
    tag_set: set,
    role_key: str,
    emotion_key: str,
    scene_key: str,
    scene: str,
    emotion: str,
    props_list: List[str],
    style: str,
    mtype: str,
    content_type: str,
    scene_intent: str = "",
    text: str = "",
    segment_no: int = 1,
    total_segments: int = 1,
    scene_description: str = "",
    career_cn: str = "",
    role_visual_keywords: Optional[List[str]] = None,
    life_elements: Optional[List[str]] = None,
    visual_prompt: str = "",
) -> Dict[str, Any]:
    try:
        generated = await generate_and_cache_dynamic_material(
            image_tags=list(tag_set),
            scene=scene_key,
            emotion=emotion,
            scene_text=scene or scene_key,
            emotion_text=emotion,
            props=props_list,
            style=style,
            material_type=mtype,
            scene_intent=scene_intent,
            segment_text=text,
            segment_no=segment_no,
            total_segments=total_segments,
            scene_description=scene_description,
            role_key=role_key,
            career_cn=career_cn,
            role_visual_keywords=role_visual_keywords,
            life_elements=life_elements,
            visual_prompt=visual_prompt,
        )
    except ImageGenerationError as err:
        msg = str(err).strip() or AI_IMAGE_FAILED_MSG
        logger.warning("[素材匹配] AI 生成失败 seg=%s: %s", segment_no, msg)
        return _missing_material(error=msg, content_type=content_type)
    except Exception as err:
        msg = f"AI配图异常：{err}"
        logger.exception("[素材匹配] AI 生成异常 seg=%s", segment_no)
        return _missing_material(error=msg, content_type=content_type)

    if not generated:
        return _missing_material(
            error="AI 生成无结果（即梦未返回图片）",
            content_type=content_type,
        )

    out = _material_result(
        generated,
        source=generated.get("source", "generated"),
        cache_hit=bool(generated.get("cacheHit")),
        material_type=mtype,
        content_type=content_type,
    )
    if scene_description:
        out["sceneDescription"] = scene_description
    return out


def match_material_catalog_sync(
    image_tags: List[str],
    *,
    role: str = "",
    emotion: str = "",
    scene: str = "",
    text: str = "",
    props: Optional[List[str]] = None,
    style: str = "",
    generate_if_missing: bool = True,
    segment_no: int = 1,
    total_segments: int = 1,
    used_material_ids: Optional[Set[str]] = None,
    used_material_urls: Optional[Set[str]] = None,
    recent_material_types: Optional[List[str]] = None,
    force_slot_type: Optional[str] = None,
    scene_intent: Optional[str] = None,
    catalog: Optional[List[Dict[str, Any]]] = None,
    used_scene_keys: Optional[Set[str]] = None,
    career_cn: str = "",
) -> Dict[str, Any]:
    """
    按文案 sceneIntent + 内容类型 + 视频节奏规划选择素材；人物仅来自已确认角色 IP。
    """
    content_type = classify_segment_content(
        text,
        emotion=emotion,
        segment_no=segment_no,
        total_segments=total_segments,
    )
    intent = normalize_scene_intent(
        scene_intent,
        text,
        emotion=emotion,
        segment_no=segment_no,
        total_segments=total_segments,
    )

    role_key = infer_role_key(role)
    strat = merged_material_strategy(
        content_type,
        intent,
        text=text,
        emotion=emotion,
        segment_no=segment_no,
        total_segments=total_segments,
        used_scene_keys=used_scene_keys,
        role_key=role_key,
        career_cn=career_cn,
    )
    if force_slot_type:
        prefer_types = slot_to_prefer_types(force_slot_type)  # type: ignore[arg-type]
        primary_mtype = prefer_types[0]
        forbid_character = force_slot_type != "character"
    else:
        prefer_types = strat["preferTypes"]
        forbid_character = strat["forbidCharacter"]
        primary_mtype = strat["primaryMaterialType"]

    tag_set = set(
        build_segment_tags(
            normalize_tags(image_tags),
            content_type,
            emotion,
            scene_intent=intent,
            text=text,
            segment_no=segment_no,
            total_segments=total_segments,
            role_key=role_key,
            career_cn=career_cn,
        )
    )
    props_list = [str(p).strip().lower() for p in (props or []) if str(p).strip()]
    for p in props_list:
        tag_set.add(p)

    emotion_key = infer_emotion_key(emotion)
    # 语义场景优先于 LLM/职业默认工位
    scene_key = normalize_scene_key(strat.get("sceneKey") or scene or "")
    for hint in strat.get("sceneHints") or []:
        tag_set.add(hint)
        for sk in scene_match_keys(hint):
            tag_set.add(sk)

    for cn, key in ROLE_CN_TO_KEY.items():
        if cn in (role or "") and key not in tag_set:
            tag_set.add(key)
    try:
        from app.ai_short_drama.profession_store import profession_store

        rk = infer_role_key(role)
        if rk and rk != "none" and profession_store.is_valid_role(rk):
            tag_set.add(rk)
            label = profession_store.role_label(rk)
            if label:
                tag_set.add(label)
    except Exception:
        pass

    logger.info(
        "[素材匹配] seg=%s content=%s intent=%s slot=%s prefer=%s text=%s",
        segment_no,
        content_type,
        intent,
        force_slot_type or "-",
        prefer_types,
        (text or "")[:24],
    )

    needs_character_ip = force_slot_type == "character" or (
        not force_slot_type and (content_type == "career" or primary_mtype == "character")
    )
    if needs_character_ip:
        ip = _resolve_character_ip_for_role(role_key)
        if ip:
            logger.info("[素材匹配] 使用角色IP role=%s id=%s", role_key, ip.get("id"))
            mat = _material_from_character_ip(ip, content_type=content_type)
            mat["plannedSlotType"] = force_slot_type or "character"
            mat["sceneIntent"] = intent
            mat["contentType"] = content_type
            return mat
        return _missing_material(
            error=CHARACTER_IP_MISSING_MSG,
            content_type=content_type,
        )

    catalog = catalog if catalog is not None else _load_catalog()

    best, best_score = _pick_best_candidate(
        catalog,
        tag_set,
        role_key,
        emotion_key,
        scene_key,
        prefer_types=prefer_types,
        forbid_character=forbid_character,
        used_material_ids=used_material_ids,
        used_material_urls=used_material_urls,
        recent_types=recent_material_types,
        career_cn=career_cn,
    )

    if best and best_score >= LIBRARY_MIN_SCORE:
        mtype = (best.get("type") or primary_mtype).lower()
        logger.info(
            "[素材匹配] 命中 type=%s id=%s score=%s",
            mtype,
            best.get("id"),
            best_score,
        )
        out = _material_result(
            best,
            source="cache" if best.get("aiGenerated") else "catalog",
            cache_hit=bool(best.get("cacheHit")),
            material_type=mtype,
            content_type=content_type,
        )
        if force_slot_type:
            out["plannedSlotType"] = force_slot_type
        out["sceneIntent"] = intent
        out["contentType"] = content_type
        return out

    # 次级类型兜底（仍禁止无脑人物）
    for fallback_type in ("scene", "ui", "effects", "props"):
        if fallback_type in prefer_types:
            continue
        fb, fb_score = _pick_best_candidate(
            catalog,
            tag_set,
            role_key,
            emotion_key,
            scene_key,
            prefer_types=[fallback_type],
            forbid_character=True,
            used_material_ids=used_material_ids,
            used_material_urls=used_material_urls,
            recent_types=recent_material_types,
        )
        if fb and fb_score >= LIBRARY_MIN_SCORE:
            out = _material_result(
                fb,
                source="catalog",
                material_type=fallback_type,
                content_type=content_type,
            )
            out["sceneIntent"] = intent
            out["contentType"] = content_type
            return out

    miss = _missing_material(content_type=content_type)
    if force_slot_type:
        miss["plannedSlotType"] = force_slot_type
    miss["sceneIntent"] = intent
    miss["contentType"] = content_type
    return miss


async def match_material_for_shot(
    image_tags: List[str],
    *,
    role: str = "",
    emotion: str = "",
    scene: str = "",
    text: str = "",
    props: Optional[List[str]] = None,
    style: str = "",
    generate_if_missing: bool = True,
    segment_no: int = 1,
    total_segments: int = 1,
    used_material_ids: Optional[Set[str]] = None,
    used_material_urls: Optional[Set[str]] = None,
    recent_material_types: Optional[List[str]] = None,
    force_slot_type: Optional[str] = None,
    scene_intent: Optional[str] = None,
    catalog: Optional[List[Dict[str, Any]]] = None,
    used_scene_keys: Optional[Set[str]] = None,
    scene_description: str = "",
    career_cn: str = "",
    role_visual_keywords: Optional[List[str]] = None,
    life_elements: Optional[List[str]] = None,
    visual_prompt: str = "",
    skip_catalog: bool = False,
) -> Dict[str, Any]:
    """素材库匹配；缺失时可选 AI 补图（scene_description 优先传入即梦）。"""
    scene_desc = (scene_description or "").strip()
    role_kws = list(role_visual_keywords or [])
    life_els = list(life_elements or [])
    v_prompt = (visual_prompt or "").strip()
    if skip_catalog:
        out = _missing_material(content_type="")
    else:
        out = match_material_catalog_sync(
            image_tags,
            role=role,
            emotion=emotion,
            scene=scene,
            text=text,
            props=props,
            style=style,
            segment_no=segment_no,
            total_segments=total_segments,
            used_material_ids=used_material_ids,
            used_material_urls=used_material_urls,
            recent_material_types=recent_material_types,
            force_slot_type=force_slot_type,
            scene_intent=scene_intent,
            catalog=catalog,
            used_scene_keys=used_scene_keys,
            career_cn=career_cn,
        )
    if not scene_desc:
        scene_desc = str(out.get("sceneDescription") or "")
    if not role_kws and isinstance(out, dict):
        role_kws = list(out.get("roleVisualKeywords") or [])
    if not life_els:
        from app.ai_short_drama.life_moment_visual import (
            life_fragments_cn,
            pick_life_fragment_slugs,
        )

        slugs = pick_life_fragment_slugs(
            str(out.get("sceneIntent") or scene_intent or ""),
            text,
            segment_no=segment_no,
        )
        life_els = [life_fragments_cn(slugs)]
    if not generate_if_missing or not _material_needs_ai(out):
        if scene_desc:
            out["sceneDescription"] = scene_desc
        return out

    content_type = str(out.get("contentType") or "monologue")
    intent = str(out.get("sceneIntent") or "")
    intent = normalize_scene_intent(
        scene_intent,
        text,
        emotion=emotion,
        segment_no=segment_no,
        total_segments=total_segments,
    )
    role_key = infer_role_key(role)
    strat = merged_material_strategy(
        classify_segment_content(
            text,
            emotion=emotion,
            segment_no=segment_no,
            total_segments=total_segments,
        ),
        intent,
        text=text,
        emotion=emotion,
        segment_no=segment_no,
        total_segments=total_segments,
        used_scene_keys=used_scene_keys,
        role_key=role_key,
        career_cn=career_cn,
    )
    primary_mtype = strat["primaryMaterialType"]
    if force_slot_type:
        primary_mtype = slot_to_prefer_types(force_slot_type)[0]  # type: ignore[arg-type]

    tag_set = set(normalize_tags(image_tags))
    props_list = [str(p).strip().lower() for p in (props or []) if str(p).strip()]
    emotion_key = infer_emotion_key(emotion)
    scene_key = normalize_scene_key(strat.get("sceneKey") or scene or "")

    if primary_mtype != "character" and force_slot_type != "character":
        ai_type = primary_mtype if primary_mtype != "effects" else "effects"
        ai_out = await _try_ai_generate(
            tag_set=tag_set,
            role_key=role_key,
            emotion_key=emotion_key,
            scene_key=scene_key,
            scene=scene,
            emotion=emotion,
            props_list=props_list,
            style=style,
            mtype=ai_type,
            content_type=content_type,
            scene_intent=intent,
            text=text,
            segment_no=segment_no,
            total_segments=total_segments,
            scene_description=scene_desc,
            career_cn=career_cn,
            role_visual_keywords=role_kws,
            life_elements=life_els,
            visual_prompt=v_prompt,
        )
        if not _material_needs_ai(ai_out):
            if force_slot_type:
                ai_out["plannedSlotType"] = force_slot_type
            return ai_out

    if force_slot_type != "character":
        ai_out = await _try_ai_generate(
            tag_set=tag_set,
            role_key=role_key,
            emotion_key=emotion_key,
            scene_key=scene_key,
            scene=scene,
            emotion=emotion,
            props_list=props_list,
            style=style,
            mtype="scene",
            content_type=content_type,
            scene_intent=intent,
            text=text,
            segment_no=segment_no,
            total_segments=total_segments,
            scene_description=scene_desc,
            career_cn=career_cn,
            role_visual_keywords=role_kws,
            life_elements=life_els,
            visual_prompt=v_prompt,
        )
        if not _material_needs_ai(ai_out):
            if force_slot_type:
                ai_out["plannedSlotType"] = force_slot_type
            return ai_out

    return out


def _material_needs_ai(mat: Dict[str, Any]) -> bool:
    url = (mat.get("url") or "").strip()
    status = mat.get("materialStatus") or ""
    return not url or status == "missing" or mat.get("id") == "material_missing"
