from __future__ import annotations

import asyncio
import logging

from fastapi import APIRouter, Body, File, Form, UploadFile

from app.ai_short_drama.character_ip_service import (
    generate_ai_candidates,
    get_role_character_ip_status,
    get_workbench_snapshot,
)
from app.ai_short_drama.character_ip_store import ROLE_LABELS, character_ip_store
from app.ai_short_drama.material_media import validate_upload_filename
from app.ai_short_drama.profession_store import profession_store
from app.ai_short_drama.schemas import (
    CharacterIpActivateEnvelope,
    CharacterIpGenerateEnvelope,
    CharacterIpListEnvelope,
    CharacterIpRecord,
    CharacterIpUploadEnvelope,
    CharacterIpWorkbenchData,
    CharacterIpWorkbenchEnvelope,
    CharacterIpDeleteEnvelope,
    CharacterIpStatus,
    CharacterIpStatusEnvelope,
    ProfessionCreateBody,
    ProfessionEnvelope,
    ProfessionListEnvelope,
    ProfessionRecord,
    ProfessionUpdateBody,
)

logger = logging.getLogger(__name__)

character_ip_router = APIRouter(prefix="/character-ip", tags=["ai-short-drama-character-ip"])


def _delete_ips_for_role(role_key: str) -> int:
    n = 0
    for item in character_ip_store.list_all(role=role_key):
        if character_ip_store.delete(item.get("id") or ""):
            n += 1
    return n


@character_ip_router.get(
    "/professions",
    response_model=ProfessionListEnvelope,
    response_model_exclude_none=True,
)
async def list_professions() -> ProfessionListEnvelope:
    raw = await asyncio.to_thread(profession_store.list_all)
    items = [ProfessionRecord(**p) for p in raw]
    return ProfessionListEnvelope(code=0, data=items)


@character_ip_router.post(
    "/professions",
    response_model=ProfessionEnvelope,
    response_model_exclude_none=True,
)
async def create_profession(body: ProfessionCreateBody = Body(...)) -> ProfessionEnvelope:
    try:
        record = profession_store.create(
            name=body.name,
            description=body.description,
            style_hint=body.styleHint,
        )
        return ProfessionEnvelope(code=0, data=ProfessionRecord(**record))
    except ValueError as err:
        return ProfessionEnvelope(code=400, message=str(err))
    except Exception as err:
        logger.exception("create profession failed")
        return ProfessionEnvelope(code=500, message=str(err) or "创建失败")


@character_ip_router.patch(
    "/professions/{profession_id}",
    response_model=ProfessionEnvelope,
    response_model_exclude_none=True,
)
async def update_profession(
    profession_id: str,
    body: ProfessionUpdateBody = Body(...),
) -> ProfessionEnvelope:
    try:
        record = profession_store.update(
            profession_id,
            name=body.name,
            description=body.description,
            style_hint=body.styleHint,
        )
        if not record:
            return ProfessionEnvelope(code=404, message="职业不存在")
        return ProfessionEnvelope(code=0, data=ProfessionRecord(**record))
    except ValueError as err:
        return ProfessionEnvelope(code=400, message=str(err))
    except Exception as err:
        logger.exception("update profession failed")
        return ProfessionEnvelope(code=500, message=str(err) or "更新失败")


@character_ip_router.delete(
    "/professions/{profession_id}",
    response_model=ProfessionEnvelope,
    response_model_exclude_none=True,
)
async def delete_profession(profession_id: str) -> ProfessionEnvelope:
    try:
        removed = profession_store.delete(profession_id)
        if not removed:
            return ProfessionEnvelope(code=404, message="职业不存在")
        role_key = str(removed.get("roleKey") or "")
        if role_key:
            _delete_ips_for_role(role_key)
        return ProfessionEnvelope(code=0, data=ProfessionRecord(**removed), message="已删除")
    except ValueError as err:
        return ProfessionEnvelope(code=400, message=str(err))
    except Exception as err:
        logger.exception("delete profession failed")
        return ProfessionEnvelope(code=500, message=str(err) or "删除失败")


@character_ip_router.get(
    "/status",
    response_model=CharacterIpStatusEnvelope,
    response_model_exclude_none=True,
)
async def character_ip_status(role: str = "") -> CharacterIpStatusEnvelope:
    rk = (role or "").strip().lower()
    if not rk:
        return CharacterIpStatusEnvelope(code=400, message="请指定职业 role")
    if not profession_store.is_valid_role(rk):
        return CharacterIpStatusEnvelope(code=400, message="无效的职业角色")
    try:
        st = get_role_character_ip_status(rk)
        return CharacterIpStatusEnvelope(code=0, data=CharacterIpStatus(**st))
    except Exception as err:
        logger.exception("character ip status failed")
        return CharacterIpStatusEnvelope(code=500, message=str(err) or "查询失败")


@character_ip_router.get(
    "/workbench",
    response_model=CharacterIpWorkbenchEnvelope,
    response_model_exclude_none=True,
)
async def character_ip_workbench() -> CharacterIpWorkbenchEnvelope:
    try:
        roles = await asyncio.to_thread(get_workbench_snapshot)
        return CharacterIpWorkbenchEnvelope(
            code=0,
            data=CharacterIpWorkbenchData(roles=roles),
        )
    except Exception as err:
        logger.exception("character ip workbench failed")
        return CharacterIpWorkbenchEnvelope(code=500, message=str(err) or "加载失败")


@character_ip_router.get(
    "",
    response_model=CharacterIpListEnvelope,
    response_model_exclude_none=True,
)
async def list_character_ips(role: str = "") -> CharacterIpListEnvelope:
    items = [CharacterIpRecord(**i) for i in character_ip_store.list_all(role=role)]
    return CharacterIpListEnvelope(code=0, data=items)


@character_ip_router.post(
    "/upload",
    response_model=CharacterIpUploadEnvelope,
    response_model_exclude_none=True,
)
async def upload_character_ip(
    file: UploadFile = File(...),
    role: str = Form(...),
) -> CharacterIpUploadEnvelope:
    rk = (role or "").strip().lower()
    if not profession_store.is_valid_role(rk):
        return CharacterIpUploadEnvelope(code=400, message="请选择有效职业")
    if not file.filename:
        return CharacterIpUploadEnvelope(code=400, message="请选择图片文件")

    upload_err = validate_upload_filename(file.filename)
    if upload_err:
        return CharacterIpUploadEnvelope(code=400, message=upload_err)

    try:
        content = await file.read()
        if not content:
            return CharacterIpUploadEnvelope(code=400, message="文件为空")
        if len(content) > 12 * 1024 * 1024:
            return CharacterIpUploadEnvelope(code=400, message="图片不能超过 12MB")

        suffix = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else "png"
        ip_id, url = character_ip_store.save_image_bytes(rk, content, suffix=suffix)
        record = character_ip_store.create_record(
            role=rk,
            base_image_url=url,
            source="uploaded",
            status="pending",
            is_active=False,
            name=f"{ROLE_LABELS.get(rk, rk)}·上传",
            ip_id=ip_id,
        )
        logger.info("[角色IP] 上传成功 role=%s id=%s", rk, ip_id)
        return CharacterIpUploadEnvelope(code=0, data=CharacterIpRecord(**record))
    except Exception as err:
        logger.exception("upload character ip failed")
        return CharacterIpUploadEnvelope(code=500, message=str(err) or "上传失败")


@character_ip_router.post(
    "/ai-generate",
    response_model=CharacterIpGenerateEnvelope,
    response_model_exclude_none=True,
)
async def ai_generate_character_ips(
    role: str = Form(...),
    description: str = Form(""),
) -> CharacterIpGenerateEnvelope:
    rk = (role or "").strip().lower()
    if not profession_store.is_valid_role(rk):
        return CharacterIpGenerateEnvelope(code=400, message="请选择有效职业")
    try:
        desc = (description or "").strip()
        logger.info(
            "[角色IP] 开始 AI 批量生成 role=%s description=%s",
            rk,
            desc[:80] if desc else "(默认)",
        )
        created = await generate_ai_candidates(rk, description=desc)
        return CharacterIpGenerateEnvelope(
            code=0,
            data=[CharacterIpRecord(**c) for c in created],
        )
    except ValueError as err:
        return CharacterIpGenerateEnvelope(code=400, message=str(err))
    except Exception as err:
        logger.exception("ai generate character ip failed")
        return CharacterIpGenerateEnvelope(code=500, message=str(err) or "AI 生成失败")


@character_ip_router.post(
    "/{ip_id}/activate",
    response_model=CharacterIpActivateEnvelope,
    response_model_exclude_none=True,
)
async def activate_character_ip(ip_id: str) -> CharacterIpActivateEnvelope:
    record = await asyncio.to_thread(character_ip_store.activate, ip_id)
    if not record:
        return CharacterIpActivateEnvelope(code=404, message="角色不存在")
    logger.info("[角色IP] 已设为当前角色 id=%s role=%s", ip_id, record.get("role"))
    return CharacterIpActivateEnvelope(code=0, data=CharacterIpRecord(**record))


@character_ip_router.delete(
    "/{ip_id}",
    response_model=CharacterIpDeleteEnvelope,
    response_model_exclude_none=True,
)
async def delete_character_ip(ip_id: str) -> CharacterIpDeleteEnvelope:
    if not character_ip_store.delete(ip_id):
        return CharacterIpDeleteEnvelope(code=404, message="角色不存在")
    return CharacterIpDeleteEnvelope(code=0, message="已删除")
