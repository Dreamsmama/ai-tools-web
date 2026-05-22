from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, File, Form, Query, UploadFile

from app.ai_short_drama.material_media import validate_upload_filename
from app.ai_short_drama.material_store import material_store
from app.ai_short_drama.material_vision_service import (
    VALID_ROLES,
    analyze_material_image,
    fallback_metadata,
)
from app.ai_short_drama.schemas import (
    MaterialAiTagData,
    MaterialAiTagEnvelope,
    MaterialCreateRequest,
    MaterialDeleteEnvelope,
    MaterialEnvelope,
    MaterialListData,
    MaterialListEnvelope,
    MaterialRecord,
    MaterialUploadData,
    MaterialUploadEnvelope,
)

logger = logging.getLogger(__name__)

materials_router = APIRouter(prefix="/materials", tags=["ai-short-drama-materials"])

ALLOWED_UPLOAD = {".png", ".jpg", ".jpeg", ".webp"}


def _enrich_material_image_meta(item: dict) -> dict:
    if item.get("imageWidth") and item.get("imageHeight"):
        return item
    from app.ai_short_drama.material_paths import url_to_disk_path
    from app.ai_short_drama.vertical_image import analyze_image_bytes

    url = (item.get("url") or "").strip()
    if not url.startswith("/uploads/"):
        return item
    path = url_to_disk_path(url)
    if not path or not path.is_file():
        return item
    try:
        info = analyze_image_bytes(path.read_bytes())
        return {**item, **info.to_meta_dict()}
    except Exception:
        return item


@materials_router.post(
    "/upload",
    response_model=MaterialUploadEnvelope,
    response_model_exclude_none=True,
)
async def upload_material_file(file: UploadFile = File(...)) -> MaterialUploadEnvelope:
    if not file.filename:
        return MaterialUploadEnvelope(code=400, message="请选择图片文件")
    upload_err = validate_upload_filename(file.filename)
    if upload_err:
        return MaterialUploadEnvelope(code=400, message=upload_err)
    try:
        content = await file.read()
        if not content:
            return MaterialUploadEnvelope(code=400, message="文件为空")
        if len(content) > 10 * 1024 * 1024:
            return MaterialUploadEnvelope(code=400, message="图片不能超过 10MB")
        saved = material_store.save_upload_file(file.filename, content)
        return MaterialUploadEnvelope(
            code=0,
            data=MaterialUploadData(
                id=saved["id"],
                url=saved["url"],
                filename=saved["filename"],
            ),
        )
    except ValueError as err:
        return MaterialUploadEnvelope(code=400, message=str(err))
    except Exception as err:
        logger.exception("upload material failed")
        return MaterialUploadEnvelope(code=500, message=str(err) or "上传失败")


@materials_router.post(
    "",
    response_model=MaterialEnvelope,
    response_model_exclude_none=True,
)
async def create_material(body: MaterialCreateRequest) -> MaterialEnvelope:
    if not (body.url or "").strip():
        return MaterialEnvelope(code=400, message="请先上传图片")
    try:
        row = material_store.create_material(body.model_dump())
        return MaterialEnvelope(code=0, data=MaterialRecord(**row))
    except Exception as err:
        logger.exception("create material failed")
        return MaterialEnvelope(code=500, message=str(err) or "保存失败")


@materials_router.post(
    "/sync-from-disk",
    response_model=MaterialListEnvelope,
    response_model_exclude_none=True,
)
async def sync_materials_from_disk() -> MaterialListEnvelope:
    """将 uploads/short-drama 下已有图片同步进素材库，并移除 public 占位 SVG 记录。"""
    try:
        from app.ai_short_drama.material_sync import reconcile_material_store

        stats = reconcile_material_store()
        n = int(stats.get("synced") or 0)
        items = material_store.list_materials()
        records = [MaterialRecord(**_enrich_material_image_meta(item)) for item in items]
        return MaterialListEnvelope(
            code=0,
            data=MaterialListData(items=records),
            message=f"已同步 {n} 条素材" if n else "素材库已是最新",
        )
    except Exception as err:
        logger.exception("sync materials from disk failed")
        return MaterialListEnvelope(code=500, message=str(err) or "同步失败")


@materials_router.get(
    "",
    response_model=MaterialListEnvelope,
    response_model_exclude_none=True,
)
async def list_materials(
    type: str = Query("", description="素材类型筛选"),
    role: str = Query("", description="职业筛选"),
    emotion: str = Query("", description="情绪筛选"),
    tag: str = Query("", description="标签关键词"),
    ai_generated: str = Query("", description="是否AI生成：true/false"),
) -> MaterialListEnvelope:
    ai_filter: Optional[bool] = None
    if ai_generated.strip().lower() == "true":
        ai_filter = True
    elif ai_generated.strip().lower() == "false":
        ai_filter = False
    try:
        from app.ai_short_drama.material_sync import is_legacy_public_material_url

        items = material_store.list_materials(
            type_filter=type.strip(),
            role_filter=role.strip(),
            emotion_filter=emotion.strip(),
            tag_keyword=tag.strip(),
            ai_generated_filter=ai_filter,
        )
        items = [i for i in items if not is_legacy_public_material_url(str(i.get("url") or ""))]
        records = [MaterialRecord(**_enrich_material_image_meta(item)) for item in items]
        return MaterialListEnvelope(code=0, data=MaterialListData(items=records))
    except Exception as err:
        logger.exception("list materials failed")
        return MaterialListEnvelope(code=500, message=str(err) or "查询失败")


@materials_router.post(
    "/ai-tag-and-save",
    response_model=MaterialAiTagEnvelope,
    response_model_exclude_none=True,
)
async def ai_tag_and_save_material(
    file: UploadFile = File(...),
    role: str = Form(...),
    name: str = Form(""),
) -> MaterialAiTagEnvelope:
    role_key = (role or "").strip().lower()
    if role_key not in VALID_ROLES:
        return MaterialAiTagEnvelope(code=400, message="请选择有效的职业角色")

    if not file.filename:
        return MaterialAiTagEnvelope(code=400, message="请选择图片文件")
    upload_err = validate_upload_filename(file.filename)
    if upload_err:
        return MaterialAiTagEnvelope(code=400, message=upload_err)

    content = await file.read()
    if not content:
        return MaterialAiTagEnvelope(code=400, message="文件为空")
    if len(content) > 10 * 1024 * 1024:
        return MaterialAiTagEnvelope(code=400, message="图片不能超过 10MB")

    from app.ai_short_drama.material_image_validate import ImageValidationError, validate_image_bytes

    try:
        validate_image_bytes(content)
    except ImageValidationError as err:
        return MaterialAiTagEnvelope(code=400, message=str(err))

    user_name = (name or "").strip()
    filename = file.filename or "upload.png"

    try:
        meta = await analyze_material_image(
            content,
            filename,
            user_role=role_key,
            user_name=user_name,
        )
        saved_file = material_store.save_upload_file(
            filename,
            content,
            type=meta["type"],
            role=meta["role"],
            emotion=meta["emotion"],
            scene=meta["scene"],
            tags=meta.get("tags"),
        )
        tag_source = meta.get("source", "fallback")

        row = material_store.create_material(
            {
                "id": saved_file["id"],
                "name": meta["name"],
                "type": meta["type"],
                "role": meta["role"],
                "emotion": meta["emotion"],
                "scene": meta["scene"],
                "url": saved_file["url"],
                "tags": meta.get("tags") or [],
                "aiGenerated": False,
            }
        )
        return MaterialAiTagEnvelope(
            code=0,
            data=MaterialAiTagData(
                material=MaterialRecord(**row),
                tagSource="ai" if tag_source == "ai" else "fallback",
                description=meta.get("description") or None,
            ),
        )
    except ValueError as err:
        return MaterialAiTagEnvelope(code=400, message=str(err))
    except Exception as err:
        logger.exception("ai tag and save failed")
        try:
            fb = fallback_metadata(role_key, user_name)
            saved_file = material_store.save_upload_file(
                filename,
                content,
                type=fb["type"],
                role=fb["role"],
                emotion=fb["emotion"],
                scene=fb["scene"],
                tags=fb.get("tags"),
            )
            row = material_store.create_material(
                {
                    "id": saved_file["id"],
                    "name": fb["name"],
                    "type": fb["type"],
                    "role": fb["role"],
                    "emotion": fb["emotion"],
                    "scene": fb["scene"],
                    "url": saved_file["url"],
                    "tags": fb.get("tags") or [],
                }
            )
            return MaterialAiTagEnvelope(
                code=0,
                data=MaterialAiTagData(
                    material=MaterialRecord(**row),
                    tagSource="fallback",
                    description=fb.get("description"),
                ),
            )
        except Exception as inner:
            logger.exception("ai tag and save ultimate fallback failed")
            return MaterialAiTagEnvelope(code=500, message=str(inner) or "AI 识别并保存失败")


@materials_router.delete(
    "/{material_id}",
    response_model=MaterialDeleteEnvelope,
    response_model_exclude_none=True,
)
async def delete_material(material_id: str) -> MaterialDeleteEnvelope:
    try:
        ok = material_store.delete_material(material_id)
        if not ok:
            return MaterialDeleteEnvelope(code=404, message="素材不存在")
        return MaterialDeleteEnvelope(code=0)
    except Exception as err:
        logger.exception("delete material failed")
        return MaterialDeleteEnvelope(code=500, message=str(err) or "删除失败")
