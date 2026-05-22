"""Application startup hooks (short-drama bootstrap, static dirs)."""

from __future__ import annotations

from pathlib import Path

from app.config import settings


def ensure_runtime_directories(backend_root: Path) -> tuple[Path, Path]:
    generated_root = backend_root / "generated"
    generated_root.mkdir(parents=True, exist_ok=True)
    (generated_root / "short-drama").mkdir(parents=True, exist_ok=True)
    (generated_root / "xiaohongshu").mkdir(parents=True, exist_ok=True)

    uploads_root = backend_root / "uploads"
    uploads_root.mkdir(parents=True, exist_ok=True)
    (uploads_root / "short-drama").mkdir(parents=True, exist_ok=True)
    return generated_root, uploads_root


def run_short_drama_startup() -> None:
    try:
        from app.ai_short_drama.material_paths import ensure_standard_layout

        ensure_standard_layout()
    except Exception:
        pass

    if settings.short_drama_startup_cleanup:
        try:
            from app.ai_short_drama.material_cleanup import scan_and_delete_invalid_assets

            n = scan_and_delete_invalid_assets()
            if n:
                print(f"[素材清理] 启动时已删除 {n} 个纯色/无效占位素材文件")
        except Exception as exc:
            print(f"[素材清理] 启动扫描跳过: {exc}")

    try:
        from app.ai_short_drama.profession_store import profession_store

        profession_store.list_all()
    except Exception as exc:
        print(f"[职业注册] 初始化跳过: {exc}")

    try:
        from app.ai_short_drama.material_sync import reconcile_material_store

        stats = reconcile_material_store()
        if stats.get("synced") or stats.get("removed_builtin"):
            print(
                f"[素材同步] uploads+{stats.get('synced', 0)} "
                f"清理占位-{stats.get('removed_builtin', 0)}"
            )
    except Exception as exc:
        print(f"[素材同步] uploads 同步跳过: {exc}")

    try:
        from app.ai_short_drama.material_bootstrap import seed_builtin_materials_if_empty

        seed_builtin_materials_if_empty()
    except Exception as exc:
        print(f"[素材引导] 内置素材导入跳过: {exc}")

    try:
        from app.ai_short_drama.character_ip_store import character_ip_store
        from app.ai_short_drama.material_store import material_store

        n = character_ip_store.migrate_from_legacy_materials(material_store.list_materials())
        if n:
            print(f"[角色IP] 已从历史人物素材迁移 {n} 个职业基础角色")
    except Exception as exc:
        print(f"[角色IP] 迁移跳过: {exc}")
