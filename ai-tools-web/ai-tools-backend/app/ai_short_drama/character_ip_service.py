from __future__ import annotations

import asyncio
import logging
from typing import Any, Dict, List

from app.ai_short_drama.character_ip_prompt import (
    CHARACTER_IP_VARIANTS,
    analyze_existing_character_diversity,
    build_prompts_for_generation,
)
from app.ai_short_drama.character_ip_store import ROLE_LABELS, character_ip_store
from app.ai_short_drama.jimeng_image_provider import (
    AI_IMAGE_FAILED_MSG,
    AI_IMAGE_TIMEOUT_SECONDS,
    ImageGenerationError,
    generate_dynamic_image,
)
from app.ai_short_drama.material_image_validate import ImageValidationError, validate_image_bytes
from app.ai_short_drama.profession_store import profession_store

logger = logging.getLogger(__name__)

# 并发生成候选图上限，避免 4 路即梦同时打满单进程事件循环
_CHARACTER_IP_PARALLEL = 2


def _ip_generate_sem() -> asyncio.Semaphore:
    """每个事件循环一个 Semaphore（兼容 uvicorn 多 worker）。"""
    loop = asyncio.get_running_loop()
    attr = "_character_ip_generate_sem"
    sem = getattr(loop, attr, None)
    if sem is None:
        sem = asyncio.Semaphore(_CHARACTER_IP_PARALLEL)
        setattr(loop, attr, sem)
    return sem


def _persist_candidate_sync(role: str, image_data: bytes, index: int) -> Dict[str, Any]:
    """校验 + 写盘 + 写 JSON（在线程池执行，避免阻塞其它 HTTP 请求）。"""
    validate_image_bytes(image_data)
    ip_id, url = character_ip_store.save_image_bytes(role, image_data)
    return character_ip_store.create_record(
        role=role,
        base_image_url=url,
        source="ai_generated",
        status="pending",
        is_active=False,
        name=f"{ROLE_LABELS.get(role, role)}·候选{chr(65 + index)}",
        ip_id=ip_id,
    )


async def _generate_one_candidate(role: str, prompt: str, index: int) -> Dict[str, Any]:
    logger.info("[角色IP] AI 生成候选 role=%s index=%s", role, index)
    try:
        sem = _ip_generate_sem()
        async with sem:
            result = await asyncio.wait_for(
                generate_dynamic_image(prompt, size="1080x1920", for_character=True),
                timeout=AI_IMAGE_TIMEOUT_SECONDS,
            )
            return await asyncio.to_thread(
                _persist_candidate_sync,
                role,
                result.data,
                index,
            )
    except (ImageGenerationError, ImageValidationError, asyncio.TimeoutError) as err:
        logger.warning("[角色IP] 候选生成失败 role=%s index=%s: %s", role, index, err)
        raise


async def generate_ai_candidates(role: str, *, description: str = "") -> List[Dict[str, Any]]:
    rk = role.strip().lower()
    if not profession_store.is_valid_role(rk):
        raise ValueError(f"不支持的职业: {role}，请先在角色管理中创建")

    desc = (description or "").strip()
    if len(desc) > 500:
        raise ValueError("描述不能超过 500 字")

    diversity = await analyze_existing_character_diversity(rk)
    prompts = build_prompts_for_generation(rk, desc, diversity=diversity)
    logger.info(
        "[角色IP] 生成 prompt role=%s 自定义描述=%s 参考职业数=%s 分析来源=%s",
        rk,
        bool(desc),
        len(diversity.reference_roles),
        diversity.source,
    )
    for i, p in enumerate(prompts):
        logger.info("[角色IP] prompt[%s] %s", i, p[:220])

    tasks = [_generate_one_candidate(rk, p, i) for i, p in enumerate(prompts)]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    created: List[Dict[str, Any]] = []
    errors: List[str] = []
    for item in results:
        if isinstance(item, Exception):
            errors.append(str(item))
        else:
            created.append(item)

    if not created:
        raise ImageGenerationError(errors[0] if errors else AI_IMAGE_FAILED_MSG)

    logger.info("[角色IP] AI 候选完成 role=%s count=%s", rk, len(created))
    return created


def get_role_character_ip_status(role_key: str) -> Dict[str, Any]:
    """单个职业的角色 IP 状态（供生成页与 API 使用）。"""
    rk = (role_key or "").strip().lower()
    active = character_ip_store.get_active(rk) if rk else None
    return {
        "role": rk,
        "roleLabel": profession_store.role_label(rk),
        "configured": active is not None,
        "baseImageUrl": (active or {}).get("baseImageUrl") or None,
        "name": (active or {}).get("name") or None,
    }


def get_workbench_snapshot() -> List[Dict[str, Any]]:
    """按职业聚合：active + pending 候选（单次读库）。"""
    by_role = character_ip_store.list_all_grouped_by_role()
    snapshot = []
    for prof in profession_store.list_all():
        role = str(prof.get("roleKey") or "")
        if not role:
            continue
        all_items = by_role.get(role, [])
        active = next(
            (
                i
                for i in all_items
                if i.get("isActive") and i.get("status") == "approved"
            ),
            None,
        )
        pending = [i for i in all_items if i.get("status") == "pending"]
        snapshot.append(
            {
                "professionId": prof.get("id"),
                "role": role,
                "roleLabel": prof.get("name") or ROLE_LABELS.get(role, role),
                "description": prof.get("description") or "",
                "styleHint": prof.get("styleHint") or "",
                "builtIn": bool(prof.get("builtIn")),
                "active": active,
                "pending": pending,
                "configured": active is not None,
            }
        )
    return snapshot
