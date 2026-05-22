from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional, Optional

import httpx

from app.ai_short_drama.json_parse import (
    normalize_segment_dict,
    try_parse_segment_payload,
)
from app.ai_short_drama.material_matcher import (
    MISSING_MATERIAL_MSG,
    _load_catalog,
    match_material_catalog_sync,
    match_material_for_shot,
)
from app.ai_short_drama.video_material_plan import plan_video_material_slots
from app.ai_short_drama.character_ip_service import get_role_character_ip_status
from app.ai_short_drama.mock_storyboard import build_mock_title
from app.ai_short_drama.role_catalog import (
    force_segments_role,
    resolve_from_user_selection,
    resolve_role_key,
)
from app.ai_short_drama.prompt import (
    build_script_analysis_messages,
    build_short_drama_messages,
)
from app.ai_short_drama.rhythm_engine import apply_auto_rhythm
from app.ai_short_drama.scene_intent import enrich_all_segments
from app.ai_short_drama.script_split import split_script_paragraphs
from app.ai_short_drama.schemas import (
    AiShortDramaData,
    AiShortDramaEnvelope,
    AiShortDramaRequest,
    CharacterIpStatus,
    MaterialMatch,
    ShortDramaShot,
    TextImageSegment,
)
from app.config import settings
from app.llm.dashscope_client import call_dashscope

logger = logging.getLogger(__name__)

SHORT_DRAMA_MAX_TOKENS = 3200
CATALOG_MATCH_TIMEOUT_SECONDS = 15.0
CATALOG_PRELOAD_TIMEOUT_SECONDS = 45.0
GENERATE_TOTAL_TIMEOUT_SECONDS = 1_800.0
AI_IMAGE_FAILED_MSG = "AI图片生成失败"


def _script_analysis_timeout() -> float:
    return max(30.0, float(settings.short_drama_script_timeout_seconds))


def _ai_material_timeout() -> float:
    return max(30.0, float(settings.short_drama_ai_material_timeout_seconds))


def _ai_material_parallel() -> int:
    return max(1, min(4, int(settings.short_drama_ai_material_parallel)))


async def _call_dashscope_short_drama(
    messages: List[Dict[str, str]],
    *,
    timeout_seconds: float | None = None,
) -> str:
    limit = timeout_seconds if timeout_seconds is not None else _script_analysis_timeout()
    return await call_dashscope(
        messages,
        temperature=0.78,
        max_tokens=SHORT_DRAMA_MAX_TOKENS,
        timeout_seconds=limit,
        connect_timeout_seconds=15.0,
    )


def _segments_to_shots(segments: List[TextImageSegment]) -> List[ShortDramaShot]:
    return [
        ShortDramaShot(
            shotNo=s.segmentNo,
            duration=s.duration,
            scene=s.scene,
            role=s.role,
            emotion=s.emotion,
            subtitle=s.text,
            imageTags=list(s.imageTags or []),
            props=list(s.props or []),
            material=s.material,
        )
        for s in segments
    ]


def _to_material_match(mat: Dict[str, Any]) -> MaterialMatch:
    src = mat.get("source", "catalog")
    if src not in (
        "catalog",
        "cache",
        "generated",
        "default",
        "placeholder",
        "missing",
        "character_ip",
    ):
        src = "catalog"
    status = mat.get("materialStatus", "ready")
    if status not in ("ready", "placeholder", "generating", "missing"):
        status = "missing" if src == "missing" else "ready"
    url = (mat.get("url") or "").strip()
    err = mat.get("materialError")
    if status == "missing" or src == "missing" or not url:
        return MaterialMatch(
            id=mat.get("id") or "material_missing",
            name=mat.get("name") or MISSING_MATERIAL_MSG,
            url="",
            tags=list(mat.get("tags") or []),
            aiGenerated=False,
            cacheHit=False,
            source="missing",
            materialStatus="missing",
            materialError=str(err or mat.get("name") or MISSING_MATERIAL_MSG),
            materialType="",
            contentType=str(mat.get("contentType") or ""),
            plannedSlotType=str(mat.get("plannedSlotType") or ""),
        )
    return MaterialMatch(
        id=mat.get("id") or "material",
        name=mat.get("name") or "",
        url=url,
        tags=list(mat.get("tags") or []),
        aiGenerated=bool(mat.get("aiGenerated")),
        cacheHit=bool(mat.get("cacheHit")),
        source=src,
        materialStatus=status,
        materialError=None,
        materialType=str(mat.get("materialType") or ""),
        contentType=str(mat.get("contentType") or ""),
        plannedSlotType=str(mat.get("plannedSlotType") or ""),
        imageWidth=mat.get("imageWidth"),
        imageHeight=mat.get("imageHeight"),
        aspectRatio=mat.get("aspectRatio"),
        isVertical=mat.get("isVertical"),
        exifOrientation=mat.get("exifOrientation"),
    )


def _material_needs_ai(mat: Dict[str, Any]) -> bool:
    url = (mat.get("url") or "").strip()
    status = mat.get("materialStatus") or ""
    return not url or status == "missing" or mat.get("id") == "material_missing"


def _error_envelope(
    message: str,
    stage: str,
    *,
    code: int = 500,
) -> AiShortDramaEnvelope:
    logger.error("[generate] failed stage=%s message=%s", stage, message)
    return AiShortDramaEnvelope(
        code=code,
        success=False,
        message=message,
        stage=stage,
        data=None,
    )


def _success_envelope(data: AiShortDramaData) -> AiShortDramaEnvelope:
    return AiShortDramaEnvelope(code=0, success=True, data=data)


async def _match_shot_catalog(
    item: Dict[str, Any],
    *,
    seg_no: int,
    total: int,
    emotion_style: str,
    used_ids: set,
    used_urls: set,
    recent_types: List[str],
    force_slot_type: Optional[str] = None,
    catalog: Optional[List[Dict[str, Any]]] = None,
    used_scene_keys: Optional[set] = None,
    career_cn: str = "",
) -> Dict[str, Any]:
    try:
        return await asyncio.wait_for(
            asyncio.to_thread(
                match_material_catalog_sync,
                item.get("imageTags") or [],
                role=item.get("role") or "",
                emotion=item.get("emotion") or "",
                scene=item.get("scene") or "",
                text=item.get("text") or "",
                props=item.get("props") or [],
                style=emotion_style,
                segment_no=seg_no,
                total_segments=total,
                used_material_ids=used_ids,
                used_material_urls=used_urls,
                recent_material_types=recent_types,
                force_slot_type=force_slot_type,
                scene_intent=item.get("sceneIntent") or "",
                catalog=catalog,
                used_scene_keys=used_scene_keys,
                career_cn=career_cn,
            ),
            timeout=CATALOG_MATCH_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.error("[generate] catalog match timeout seg=%s", seg_no)
        from app.ai_short_drama.material_matcher import _missing_material

        return _missing_material(
            error="素材库匹配超时",
            content_type="",
        )


async def _match_shot_ai(
    item: Dict[str, Any],
    *,
    seg_no: int,
    total: int,
    emotion_style: str,
    used_ids: set,
    used_urls: set,
    recent_types: List[str],
    force_slot_type: Optional[str] = None,
    catalog: Optional[List[Dict[str, Any]]] = None,
    used_scene_keys: Optional[set] = None,
    career_cn: str = "",
    scene_description: str = "",
    scene_intent: str = "",
    role_visual_keywords: Optional[List[str]] = None,
    life_elements: Optional[List[str]] = None,
    visual_prompt: str = "",
    skip_catalog: bool = False,
) -> Dict[str, Any]:
    scene_desc = (scene_description or item.get("sceneDescription") or "").strip()
    intent = (scene_intent or item.get("sceneIntent") or "").strip()
    role_kws = role_visual_keywords
    if role_kws is None:
        raw = item.get("roleVisualKeywords") or item.get("role_visual_keywords")
        role_kws = list(raw) if isinstance(raw, list) else []
    life_els = life_elements
    if life_els is None:
        raw_life = item.get("lifeElements") or item.get("lifeFragments") or item.get("life_elements")
        if isinstance(raw_life, list):
            life_els = list(raw_life)
        else:
            life_els = []
    v_prompt = (visual_prompt or item.get("visualPrompt") or item.get("visual_prompt") or "").strip()

    try:
        return await asyncio.wait_for(
            match_material_for_shot(
                item.get("imageTags") or [],
                role=item.get("role") or "",
                emotion=item.get("emotion") or "",
                scene=item.get("scene") or "",
                text=item.get("text") or "",
                props=item.get("props") or [],
                style=emotion_style,
                generate_if_missing=True,
                segment_no=seg_no,
                total_segments=total,
                used_material_ids=used_ids,
                used_material_urls=used_urls,
                recent_material_types=recent_types,
                force_slot_type=force_slot_type,
                scene_intent=intent,
                catalog=catalog,
                used_scene_keys=used_scene_keys,
                scene_description=scene_desc,
                career_cn=career_cn,
                role_visual_keywords=role_kws,
                life_elements=life_els,
                visual_prompt=v_prompt,
                skip_catalog=skip_catalog,
            ),
            timeout=_ai_material_timeout(),
        )
    except asyncio.TimeoutError:
        logger.error("[generate] AI material timeout seg=%s", seg_no)
        from app.ai_short_drama.material_matcher import _missing_material

        return _missing_material(
            error=f"AI 配图超时（>{int(_ai_material_timeout())}秒）",
            content_type="",
        )


def _track_material_usage(
    mat: Dict[str, Any],
    used_ids: set,
    used_urls: set,
    recent_types: List[str],
) -> None:
    mid = mat.get("id") or ""
    url = (mat.get("url") or "").strip()
    mtype = (mat.get("materialType") or "").lower()
    if mid and mid != "material_missing" and url:
        used_ids.add(mid)
        used_urls.add(url)
    if mtype:
        recent_types.append(mtype)


def _segments_with_missing_materials(
    raw_segments: List[Dict[str, Any]],
    *,
    error: str = MISSING_MATERIAL_MSG,
) -> List[TextImageSegment]:
    """素材阶段整体失败时仍返回可预览的分镜（配图标记为缺失）。"""
    from app.ai_short_drama.material_matcher import _missing_material

    out: List[TextImageSegment] = []
    for item in sorted(raw_segments, key=lambda x: int(x.get("segmentNo", 0))):
        seg_no = int(item.get("segmentNo", len(out) + 1))
        mat = _missing_material(error=error, content_type="")
        out.append(
            TextImageSegment(
                segmentNo=seg_no,
                duration=item["duration"],
                text=item["text"],
                role=item["role"],
                emotion=item["emotion"],
                scene=item["scene"],
                sceneIntent=str(item.get("sceneIntent") or ""),
                imageTags=item.get("imageTags") or [],
                props=item.get("props") or [],
                contentType="",
                material=_to_material_match(mat),
            )
        )
    return out


async def _attach_materials(
    raw_segments: List[Dict[str, Any]],
    *,
    emotion_style: str = "",
    generate_dynamic: bool = True,
    career_cn: str = "",
) -> List[TextImageSegment]:
    """两阶段：素材库匹配 → AI 补图（失败不阻塞，标记 missing）。"""
    sorted_items = sorted(raw_segments, key=lambda x: int(x.get("segmentNo", 0)))
    total = len(sorted_items)
    used_ids: set = set()
    used_urls: set = set()
    used_scene_keys: set = set()
    recent_types: List[str] = []

    video_plan = plan_video_material_slots(sorted_items)
    try:
        catalog = await asyncio.wait_for(
            asyncio.to_thread(lambda: _load_catalog(force_refresh=True)),
            timeout=CATALOG_PRELOAD_TIMEOUT_SECONDS,
        )
    except asyncio.TimeoutError:
        logger.warning(
            "[generate] catalog preload timeout %.0fs, use cache",
            CATALOG_PRELOAD_TIMEOUT_SECONDS,
        )
        catalog = await asyncio.to_thread(lambda: _load_catalog(force_refresh=False))
    logger.info(
        "[generate] start material matching segments=%s catalog_items=%s",
        total,
        len(catalog),
    )
    pending: List[tuple[Dict[str, Any], Dict[str, Any], int]] = []
    for item in sorted_items:
        seg_no = int(item.get("segmentNo", len(pending) + 1))
        slot_info = video_plan.get(seg_no) or {}
        force_slot = slot_info.get("slotType")
        try:
            mat = await _match_shot_catalog(
                item,
                seg_no=seg_no,
                total=total,
                emotion_style=emotion_style,
                used_ids=used_ids,
                used_urls=used_urls,
                recent_types=recent_types,
                force_slot_type=force_slot,
                catalog=catalog,
                used_scene_keys=used_scene_keys,
                career_cn=career_cn,
            )
        except Exception as err:
            logger.exception("[generate] catalog match failed seg=%s: %s", seg_no, err)
            from app.ai_short_drama.material_matcher import _missing_material

            mat = _missing_material(error="素材库匹配失败", content_type="")
        # 去重改写的 segment 跳过 catalog 结果，强制 AI 生图使用新的 sceneDescription
        if item.get("sceneDescriptionSource") == "dedup_rewrite":
            from app.ai_short_drama.material_matcher import _missing_material
            mat = _missing_material(content_type=str(item.get("contentType") or ""))
        _track_material_usage(mat, used_ids, used_urls, recent_types)
        sk = str(mat.get("scene") or item.get("scene") or "")
        if sk:
            used_scene_keys.add(sk)
        pending.append((item, mat, seg_no))
    logger.info("[generate] material matching done")

    if generate_dynamic:
        logger.info(
            "[generate] start ai material generation parallel=%s",
            _ai_material_parallel(),
        )
        usage_lock = asyncio.Lock()

        async def _ai_one(idx: int) -> tuple[int, Dict[str, Any]]:
            item, mat, seg_no = pending[idx]
            if not _material_needs_ai(mat):
                return idx, mat
            logger.info("[generate] AI gen seg=%s", seg_no)
            slot_info = video_plan.get(seg_no) or {}
            async with usage_lock:
                snap_ids = set(used_ids)
                snap_urls = set(used_urls)
                snap_types = list(recent_types)
            try:
                ai_mat = await _match_shot_ai(
                    item,
                    seg_no=seg_no,
                    total=total,
                    emotion_style=emotion_style,
                    used_ids=snap_ids,
                    used_urls=snap_urls,
                    recent_types=snap_types,
                    force_slot_type=slot_info.get("slotType"),
                    catalog=catalog,
                    used_scene_keys=used_scene_keys,
                    career_cn=career_cn,
                    scene_description=str(item.get("sceneDescription") or ""),
                    scene_intent=str(item.get("sceneIntent") or ""),
                    role_visual_keywords=item.get("roleVisualKeywords"),
                    life_elements=item.get("lifeFragments") or item.get("lifeElements"),
                    visual_prompt=str(item.get("visualPrompt") or ""),
                    skip_catalog=item.get("sceneDescriptionSource") == "dedup_rewrite",
                )
            except Exception as err:
                logger.exception("[generate] AI gen failed seg=%s: %s", seg_no, err)
                from app.ai_short_drama.material_matcher import _missing_material

                ai_mat = _missing_material(
                    error=str(err) or AI_IMAGE_FAILED_MSG,
                    content_type=str(mat.get("contentType") or ""),
                )
            if _material_needs_ai(ai_mat):
                # dedup_rewrite 段落 Jimeng 失败时，用更新后的 imageTags 做 catalog 兜底
                # 更新后的 imageTags 已移除职业 tag（programmer/vscode/desk），添加了生活场景 tag
                # catalog 会优先匹配 corridor/street/subway 等生活素材，避免再次命中工作站
                if item.get("sceneDescriptionSource") == "dedup_rewrite":
                    try:
                        fallback = await _match_shot_catalog(
                            item,
                            seg_no=seg_no,
                            total=total,
                            emotion_style=emotion_style,
                            used_ids=snap_ids,
                            used_urls=snap_urls,
                            recent_types=snap_types,
                            force_slot_type=slot_info.get("slotType"),
                            catalog=catalog,
                            used_scene_keys=used_scene_keys,
                            career_cn=career_cn,
                        )
                        if not _material_needs_ai(fallback):
                            ai_mat = fallback
                            logger.info("[generate] dedup catalog fallback seg=%s", seg_no)
                    except Exception:
                        pass
            if _material_needs_ai(ai_mat):
                err_msg = (ai_mat.get("materialError") or AI_IMAGE_FAILED_MSG).strip()
                from app.ai_short_drama.material_matcher import _missing_material

                ai_mat = _missing_material(
                    error=err_msg,
                    content_type=str(mat.get("contentType") or ""),
                )
            else:
                async with usage_lock:
                    _track_material_usage(ai_mat, used_ids, used_urls, recent_types)
            return idx, ai_mat

        sem = asyncio.Semaphore(_ai_material_parallel())

        async def _run(idx: int) -> tuple[int, Dict[str, Any]]:
            async with sem:
                return await _ai_one(idx)

        ai_indices = [
            idx for idx, (_, mat, _) in enumerate(pending) if _material_needs_ai(mat)
        ]
        if ai_indices:
            results = await asyncio.gather(*[_run(i) for i in ai_indices])
            for idx, ai_mat in results:
                item, _, seg_no = pending[idx]
                pending[idx] = (item, ai_mat, seg_no)
        logger.info("[generate] ai material generation done")
    else:
        logger.info("[generate] skip ai material generation (disabled)")

    segments: List[TextImageSegment] = []
    for item, mat, seg_no in pending:
        segments.append(
            TextImageSegment(
                segmentNo=seg_no,
                duration=item["duration"],
                text=item["text"],
                role=item["role"],
                emotion=item["emotion"],
                scene=item["scene"],
                sceneIntent=str(item.get("sceneIntent") or mat.get("sceneIntent") or ""),
                sceneDescription=str(item.get("sceneDescription") or ""),
                sceneDescriptionSource=str(item.get("sceneDescriptionSource") or ""),
                imageTags=item.get("imageTags") or [],
                props=item.get("props") or [],
                contentType=str(mat.get("contentType") or ""),
                material=_to_material_match(mat),
            )
        )
    return segments


def _parse_ai_segments(
    raw: str,
    role_key: str,
    *,
    career_cn: str = "",
) -> tuple[str, List[Dict[str, Any]]]:
    payload = try_parse_segment_payload(raw)
    if not payload or not payload.get("segments"):
        raise ValueError("无法解析图文段落 JSON")

    rk = (role_key or "").strip().lower() or resolve_role_key(career_cn, "")
    cn = (career_cn or "").strip()

    normalized: List[Dict[str, Any]] = []
    for idx, item in enumerate(payload["segments"]):
        if not isinstance(item, dict):
            continue
        normalized.append(normalize_segment_dict(item, idx, rk))

    if len(normalized) < 3:
        raise ValueError(f"段落数量不足：{len(normalized)} < 3")

    title = (payload.get("title") or "").strip()
    return title, enrich_all_segments(normalized[:50], career_cn=cn, role_key=rk)


def _build_data(
    title: str,
    segments: List[TextImageSegment],
    source: str,
    *,
    emotion_style: str = "",
    estimated_duration_seconds: int = 0,
    detected_career: str = "",
    detected_role: str = "",
) -> AiShortDramaData:
    style = (emotion_style or "").strip() or None
    est = int(estimated_duration_seconds) if estimated_duration_seconds > 0 else None
    if est is None and segments:
        est = sum(int(s.duration) for s in segments)
    role_key = (detected_role or "").strip().lower()
    if not role_key and segments:
        role_key = str(segments[0].role or "").strip().lower()
    career_cn = (detected_career or "").strip()
    ip_raw = get_role_character_ip_status(role_key) if role_key else None
    character_ip = CharacterIpStatus(**ip_raw) if ip_raw and role_key else None
    return AiShortDramaData(
        title=title,
        source=source,
        emotionStyle=style,
        estimatedDurationSeconds=est,
        detectedCareer=career_cn or None,
        detectedRole=role_key or None,
        characterIp=character_ip,
        segments=segments,
        shots=_segments_to_shots(segments),
    )


def _apply_user_role_selection(
    segments: List[Dict[str, Any]],
    career_hint: str,
) -> str:
    """用户在下拉框选了职业时，以该职业为唯一 role 来源（覆盖 AI 输出）。"""
    rk = resolve_from_user_selection(career_hint)
    if rk:
        force_segments_role(segments, rk)
    return rk


def _fallback_segments_from_script(
    script: str,
    *,
    career_cn: str,
) -> tuple[str, List[Dict[str, Any]]]:
    """AI 解析失败时，用规则拆段 + 默认元数据。"""
    texts = split_script_paragraphs(script)
    if not texts:
        raise ValueError("文案为空或无法拆段")

    role_key = resolve_role_key(career_cn, "")

    raw: List[Dict[str, Any]] = []
    for idx, text in enumerate(texts[:50]):
        raw.append(
            normalize_segment_dict(
                {
                    "segmentNo": idx + 1,
                    "text": text,
                    "role": role_key,
                    "emotion": "normal",
                    "scene": "office_day",
                    "imageTags": [role_key, "office_day", "normal"],
                },
                idx,
                role_key,
                max_text_len=80,
            )
        )
    title = (texts[0][:18] + "…") if texts and len(texts[0]) > 20 else (texts[0] if texts else "职业观察局")
    return title, enrich_all_segments(raw, career_cn=career_cn, role_key=role_key)


def _parse_script_segments(
    raw: str,
    *,
    career_hint: str,
) -> tuple[str, str, str, List[Dict[str, Any]]]:
    """解析文案分析 AI 返回。返回 title, career_cn, emotion_style, segments。"""
    payload = try_parse_segment_payload(raw)
    if not payload or not payload.get("segments"):
        raise ValueError("无法解析文案分析 JSON")

    if career_hint:
        career_cn = career_hint
        role_key = resolve_from_user_selection(career_hint) or resolve_role_key(career_hint, "")
    else:
        career_cn = (payload.get("detectedCareer") or "").strip()
        role_key = resolve_role_key(
            career_cn,
            str(payload.get("detectedRole") or ""),
        )

    emotion_style = (payload.get("emotionStyle") or "真实").strip() or "真实"

    normalized: List[Dict[str, Any]] = []
    for idx, item in enumerate(payload["segments"]):
        if not isinstance(item, dict):
            continue
        normalized.append(normalize_segment_dict(item, idx, role_key, max_text_len=80))

    if career_hint:
        applied = _apply_user_role_selection(normalized, career_hint)
        if applied:
            role_key = applied

    if len(normalized) < 1:
        raise ValueError("段落为空")

    title = (payload.get("title") or "").strip()
    return title, career_cn, emotion_style, enrich_all_segments(
        normalized[:50], career_cn=career_cn, role_key=role_key
    )


async def _generate_from_script(body: AiShortDramaRequest) -> AiShortDramaEnvelope:
    script = (body.script or "").strip()
    if not script:
        return _error_envelope("请粘贴完整职业观察局文案", "script_analysis", code=400)
    if len(script) < 20:
        return _error_envelope("文案过短，请粘贴完整图文文案", "script_analysis", code=400)

    career_hint = (body.career or "").strip()
    pre_split = split_script_paragraphs(script)
    form = {
        "script": script,
        "career": career_hint,
    }

    ai_title = ""
    career_cn = career_hint
    emotion_style = "真实"
    raw_segments: List[Dict[str, Any]] = []
    role_key = ""

    analysis_timeout = _script_analysis_timeout()
    try:
        logger.info(
            "[generate] start script analysis pre_split=%s timeout=%ss",
            len(pre_split),
            int(analysis_timeout),
        )
        messages = build_script_analysis_messages(form, pre_split=pre_split)
        raw = await asyncio.wait_for(
            _call_dashscope_short_drama(messages, timeout_seconds=analysis_timeout),
            timeout=analysis_timeout + 5.0,
        )
        ai_title, career_cn, emotion_style, raw_segments = _parse_script_segments(
            raw,
            career_hint=career_hint,
        )
        if career_hint:
            role_key = resolve_from_user_selection(career_hint)
        else:
            role_key = resolve_role_key(career_cn, "")
        logger.info(
            "[generate] script analysis done career=%s roleKey=%s segments=%s",
            career_cn,
            role_key,
            len(raw_segments),
        )
    except (asyncio.TimeoutError, httpx.TimeoutException) as err:
        logger.warning("[generate] script AI timeout, fallback: %s", err)
        try:
            fb_career = career_hint or career_cn
            ai_title, raw_segments = _fallback_segments_from_script(
                script,
                career_cn=fb_career,
            )
            career_cn = fb_career
            emotion_style = "真实"
        except ValueError as fb_err:
            return _error_envelope(
                f"文案分析超时（{int(analysis_timeout)}秒）且规则拆段失败：{fb_err}",
                "script_analysis",
            )
    except (ValueError, RuntimeError) as err:
        logger.warning("[generate] script AI parse failed, fallback: %s", err)
        try:
            fb_career = career_hint or career_cn
            ai_title, raw_segments = _fallback_segments_from_script(
                script,
                career_cn=fb_career,
            )
            career_cn = fb_career
            emotion_style = "真实"
        except ValueError as fb_err:
            return _error_envelope(str(fb_err), "script_analysis", code=400)
    except httpx.HTTPError as err:
        return _error_envelope(f"文案分析请求失败：{err}", "script_analysis")
    except Exception as err:
        logger.exception("[generate] script analysis unexpected error")
        return _error_envelope(str(err) or "文案分析失败", "script_analysis")

    raw_segments, estimated_total = apply_auto_rhythm(raw_segments)
    logger.info("[generate] auto rhythm applied segments=%s total_sec=%s", len(raw_segments), estimated_total)

    if career_hint:
        role_key = _apply_user_role_selection(raw_segments, career_hint) or resolve_from_user_selection(
            career_hint
        )
        career_cn = career_hint
        raw_segments = enrich_all_segments(raw_segments, career_cn=career_cn, role_key=role_key)
        logger.info("[generate] materials use selected career=%s roleKey=%s", career_cn, role_key)
    elif not role_key:
        role_key = resolve_role_key(career_cn or "", "")
        raw_segments = enrich_all_segments(raw_segments, career_cn=career_cn, role_key=role_key)

    from app.ai_short_drama.visual_dedup import deduplicate_visual_scenes
    raw_segments = deduplicate_visual_scenes(raw_segments)

    try:
        segments = await _attach_materials(
            raw_segments,
            emotion_style=emotion_style,
            generate_dynamic=body.generate_dynamic_materials,
            career_cn=career_cn,
        )
    except Exception as err:
        logger.exception("[generate] material_generation unexpected error, fallback: %s", err)
        segments = _segments_with_missing_materials(
            raw_segments,
            error="部分素材匹配失败，可稍后重试或关闭 AI 补图",
        )

    if not segments:
        return _error_envelope("段落为空", "material_generation")

    title = ai_title or build_mock_title(career_cn or "职业观察局", (script[:12] + "…") if len(script) > 12 else script)
    if not role_key:
        role_key = resolve_role_key(career_cn or "", "")
    return _success_envelope(
        _build_data(
            title,
            segments,
            "ai",
            emotion_style=emotion_style,
            estimated_duration_seconds=estimated_total,
            detected_career=career_cn,
            detected_role=role_key,
        )
    )


async def _generate_from_ai_params(body: AiShortDramaRequest) -> AiShortDramaEnvelope:
    career = (body.career or "").strip()
    theme = (body.theme or "").strip()
    emotion_style = (body.emotion_style or "").strip()
    if not career:
        return _error_envelope("请选择职业角色", "copywriting", code=400)
    if not theme:
        return _error_envelope("请填写主题", "copywriting", code=400)
    if not emotion_style:
        return _error_envelope("请选择情绪风格", "copywriting", code=400)

    form = {
        "career": career,
        "theme": theme,
        "emotion_style": emotion_style,
    }

    raw_segments: List[Dict[str, Any]]
    ai_title: str

    try:
        logger.info("[generate] start copywriting (ai mode)")
        messages = build_short_drama_messages(form)
        copy_timeout = _script_analysis_timeout()
        raw = await asyncio.wait_for(
            _call_dashscope_short_drama(messages, timeout_seconds=copy_timeout),
            timeout=copy_timeout + 5.0,
        )
        role_key = resolve_from_user_selection(career) or resolve_role_key(career, "")
        ai_title, raw_segments = _parse_ai_segments(raw, role_key, career_cn=career)
        role_key = _apply_user_role_selection(raw_segments, career) or role_key
        raw_segments = enrich_all_segments(raw_segments, career_cn=career, role_key=role_key)
        logger.info(
            "[generate] copywriting done title=%s segments=%s",
            (ai_title or "")[:40],
            len(raw_segments),
        )
    except asyncio.TimeoutError:
        return _error_envelope(
            f"文案生成超时（{int(_script_analysis_timeout())}秒），请稍后重试",
            "copywriting",
        )
    except httpx.TimeoutException:
        return _error_envelope("文案生成超时，请检查网络或 DashScope 配置", "copywriting")
    except httpx.HTTPError as err:
        return _error_envelope(f"文案生成请求失败：{err}", "copywriting")
    except ValueError as err:
        return _error_envelope(str(err), "copywriting")
    except RuntimeError as err:
        return _error_envelope(str(err), "copywriting")
    except Exception as err:
        logger.exception("[generate] copywriting unexpected error")
        return _error_envelope(str(err) or "文案生成失败", "copywriting")

    raw_segments, estimated_total = apply_auto_rhythm(raw_segments)
    logger.info("[generate] auto rhythm applied segments=%s total_sec=%s", len(raw_segments), estimated_total)

    role_key = _apply_user_role_selection(raw_segments, career) or resolve_from_user_selection(career)
    raw_segments = enrich_all_segments(raw_segments, career_cn=career, role_key=role_key)

    from app.ai_short_drama.visual_dedup import deduplicate_visual_scenes
    raw_segments = deduplicate_visual_scenes(raw_segments)

    try:
        segments = await _attach_materials(
            raw_segments,
            emotion_style=emotion_style,
            generate_dynamic=body.generate_dynamic_materials,
            career_cn=career,
        )
    except Exception as err:
        logger.exception("[generate] material_generation unexpected error, fallback: %s", err)
        segments = _segments_with_missing_materials(
            raw_segments,
            error="部分素材匹配失败，可稍后重试或关闭 AI 补图",
        )

    if not segments:
        return _error_envelope("段落为空", "material_generation")

    title = ai_title or build_mock_title(career, theme)
    if not role_key:
        role_key = resolve_role_key(career, "")
    return _success_envelope(
        _build_data(
            title,
            segments,
            "ai",
            emotion_style=emotion_style,
            estimated_duration_seconds=estimated_total,
            detected_career=career,
            detected_role=role_key,
        )
    )


async def generate_short_drama(body: AiShortDramaRequest) -> AiShortDramaEnvelope:
    mode = (body.input_mode or "script").strip().lower()
    logger.info("[generate] pipeline start mode=%s", mode)

    async def _run() -> AiShortDramaEnvelope:
        if mode == "script":
            return await _generate_from_script(body)
        return await _generate_from_ai_params(body)

    try:
        return await asyncio.wait_for(_run(), timeout=GENERATE_TOTAL_TIMEOUT_SECONDS)
    except asyncio.TimeoutError:
        logger.error(
            "[generate] total timeout after %.0fs",
            GENERATE_TOTAL_TIMEOUT_SECONDS,
        )
        return _error_envelope(
            f"生成超时（超过 {int(GENERATE_TOTAL_TIMEOUT_SECONDS // 60)} 分钟），"
            "请缩短文案、关闭 AI 补图或稍后重试。",
            "material_generation",
            code=504,
        )
