from __future__ import annotations

from typing import Any, Dict, List

from app.ai_short_drama.material_infer import ROLE_CN_TO_KEY
from app.ai_short_drama.profession_store import profession_store

# 历史内置职业（用于清洗 AI 误标的 tag）
LEGACY_BUILTIN_ROLE_KEYS = frozenset(
    {"programmer", "product_manager", "hr", "tester", "devops", "sales", "none"}
)


def all_registered_role_keys() -> frozenset[str]:
    keys = {
        str(p.get("roleKey") or "").strip().lower()
        for p in profession_store.list_all()
        if p.get("roleKey")
    }
    return frozenset(keys)


def default_role_key() -> str:
    items = profession_store.list_all()
    if items:
        return str(items[0].get("roleKey") or "programmer")
    return "programmer"


def resolve_role_key(career_cn: str, role_hint: str = "") -> str:
    """
    将用户选择的中文职业名或 roleKey 解析为素材/角色 IP 使用的 roleKey。
    用户明确选择的职业名优先于 AI 返回的 role_hint。
    """
    cn = (career_cn or "").strip()
    if cn:
        resolved = profession_store.resolve_career_cn(cn)
        if resolved:
            return resolved
        low = cn.lower()
        if profession_store.is_valid_role(low):
            return low
        legacy = ROLE_CN_TO_KEY.get(cn) or ROLE_CN_TO_KEY.get(cn.upper())
        if legacy:
            return legacy

    key = (role_hint or "").strip().lower()
    if key and profession_store.is_valid_role(key):
        return key
    if key in LEGACY_BUILTIN_ROLE_KEYS:
        return key
    return default_role_key()


def resolve_from_user_selection(career_cn: str) -> str:
    """仅根据用户在下拉框选择的职业名解析（生成页专用）。"""
    cn = (career_cn or "").strip()
    if not cn:
        return ""
    return resolve_role_key(cn, "")


def force_segments_role(segments: List[Dict[str, Any]], role_key: str) -> None:
    """用户已选职业时：全片段落 role/imageTags 与所选职业一致。"""
    rk = (role_key or "").strip().lower()
    if not rk:
        return
    known = all_registered_role_keys() | LEGACY_BUILTIN_ROLE_KEYS
    for seg in segments:
        seg["role"] = rk
        tags = [str(t).strip().lower() for t in (seg.get("imageTags") or []) if str(t).strip()]
        kept = [t for t in tags if t not in known and t != rk]
        seg["imageTags"] = ([rk] + kept)[:12]


def prompt_role_catalog_block() -> str:
    """供 LLM 参考的职业表（来自职业注册表，非写死）。"""
    lines: List[str] = []
    for p in profession_store.list_all():
        name = (p.get("name") or "").strip()
        rk = (p.get("roleKey") or "").strip()
        if name and rk:
            lines.append(f'  - "{name}" → role="{rk}"')
    return "\n".join(lines) if lines else f'  - "程序员" → role="{default_role_key()}"'


def prompt_user_career_instruction(career_cn: str) -> str:
    """用户已选职业时注入 prompt 的硬性约束。"""
    from app.ai_short_drama.role_visual_keywords import prompt_role_visual_block

    cn = (career_cn or "").strip()
    if not cn:
        return ""
    rk = resolve_from_user_selection(cn)
    visual_block = prompt_role_visual_block(rk, cn)
    if not rk:
        return f"用户已选择职业：{cn}。全片 detectedRole 与各段 role 必须对应该职业。{visual_block}"
    label = profession_store.role_label(rk)
    return (
        f"用户已选择职业：{cn}（role=\"{rk}\"）。"
        f"全片所有段落的 role 字段必须 exactly 为 \"{rk}\"，"
        f"detectedRole 必须为 \"{rk}\"，detectedCareer 必须为 \"{label or cn}\"；"
        f"禁止使用其他职业的 role（例如不要用 hr 代替 {cn}）。"
        f"{visual_block}"
    )
