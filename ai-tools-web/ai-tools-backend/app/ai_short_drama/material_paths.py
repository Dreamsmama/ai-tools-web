from __future__ import annotations

import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

BACKEND_ROOT = Path(__file__).resolve().parent.parent.parent
UPLOAD_ROOT = BACKEND_ROOT / "uploads" / "short-drama"
UPLOAD_URL_PREFIX = "/uploads/short-drama"

VALID_ROLES = frozenset(
    {"programmer", "product_manager", "hr", "tester", "devops", "sales"}
)
VALID_EMOTIONS = frozenset(
    {
        "normal",
        "calm",
        "tired",
        "stressed",
        "shocked",
        "angry",
        "happy",
        "confused",
        "none",
    }
)
VALID_SCENES = frozenset(
    {
        "night_office",
        "office_night",
        "office_day",
        "office",
        "meeting_room",
        "desk",
        "workstation",
        "interview_room",
        "server_room",
        "none",
    }
)
VALID_TYPES = frozenset({"character", "scene", "ui", "props", "effects", "placeholder"})

PROP_TAG_DIRS: Dict[str, str] = {
    "coffee": "coffee",
    "phone": "phone",
    "work_card": "work-card",
    "work-card": "work-card",
    "terminal": "terminal",
    "linux": "terminal",
    "linux_terminal": "terminal",
}

# UI 子目录：标签 key → 目录名
UI_TAG_DIRS: Dict[str, str] = {
    "error_log": "error-log",
    "error-log": "error-log",
    "feishu": "feishu",
    "jira": "jira",
    "alarm": "alarm",
}

PROP_TAGS = frozenset(PROP_TAG_DIRS.keys()) | frozenset(PROP_TAG_DIRS.values())
UI_TAGS = frozenset(UI_TAG_DIRS.keys()) | frozenset(v for v in UI_TAG_DIRS.values())

# 启动时预创建的目录骨架（空目录，便于浏览与后续随机抽取）
STANDARD_REL_DIRS: Tuple[str, ...] = (
    "characters/programmer/tired",
    "characters/programmer/angry",
    "characters/programmer/shocked",
    "characters/programmer/normal",
    "characters/product-manager/tired",
    "characters/product-manager/normal",
    "characters/hr/tired",
    "characters/hr/normal",
    "characters/tester/tired",
    "characters/tester/normal",
    "characters/devops/tired",
    "characters/devops/normal",
    "characters/sales/tired",
    "characters/sales/normal",
    "scenes/night-office",
    "scenes/office-night",
    "scenes/office-day",
    "scenes/meeting-room",
    "scenes/desk",
    "scenes/workstation",
    "scenes/interview-room",
    "scenes/server-room",
    "scenes/office",
    "placeholders",
    "ui/error-log",
    "ui/feishu",
    "ui/jira",
    "ui/alarm",
    "ui/misc",
    "props/coffee",
    "props/phone",
    "props/work-card",
    "props/terminal",
    "effects",
)


def enum_to_slug(value: str) -> str:
    """枚举值转目录段：product_manager → product-manager"""
    v = (value or "").strip().lower()
    if not v or v == "none":
        return ""
    return v.replace("_", "-")


def _pick_enum(value: str, allowed: frozenset, default: str = "") -> str:
    v = (value or "").strip().lower()
    return v if v in allowed else default


def _random_suffix(length: int = 4) -> str:
    return uuid.uuid4().hex[:length]


def _infer_ui_subdir(tags: Optional[List[str]]) -> str:
    for raw in tags or []:
        key = str(raw).strip().lower().replace("-", "_")
        if key in UI_TAG_DIRS:
            return UI_TAG_DIRS[key]
        hyphen = key.replace("_", "-")
        if hyphen in UI_TAG_DIRS.values():
            return hyphen
    return "misc"


def resolve_storage_rel_dir(
    *,
    type: str = "character",
    role: str = "none",
    emotion: str = "none",
    scene: str = "none",
    tags: Optional[List[str]] = None,
    props: Optional[List[str]] = None,
) -> str:
    """
    根据素材元数据返回相对 uploads/short-drama 的子目录（无首尾斜杠）。
    character → characters/{role}/{emotion}
    scene     → scenes/{scene}
    ui        → ui/{tag-derived}
    其他      → placeholders
    """
    mtype = _pick_enum(type, VALID_TYPES, "character")

    if mtype == "character":
        role_key = _pick_enum(role, VALID_ROLES, "programmer")
        emotion_key = _pick_enum(emotion, VALID_EMOTIONS, "normal") or "normal"
        if emotion_key == "none":
            emotion_key = "normal"
        return f"characters/{enum_to_slug(role_key)}/{enum_to_slug(emotion_key)}"

    if mtype == "scene":
        scene_key = _pick_enum(scene, VALID_SCENES, "office") or "office"
        if scene_key == "none":
            scene_key = "office"
        return f"scenes/{enum_to_slug(scene_key)}"

    if mtype == "ui":
        return f"ui/{_infer_ui_subdir(tags)}"

    if mtype == "props":
        return f"props/{_infer_prop_subdir(tags, props)}"

    if mtype == "effects":
        return "effects"

    return "placeholders"


def _infer_prop_subdir(tags: Optional[List[str]], props: Optional[List[str]] = None) -> str:
    for raw in list(props or []) + list(tags or []):
        key = str(raw).strip().lower().replace("-", "_")
        if key in PROP_TAG_DIRS:
            return PROP_TAG_DIRS[key]
    return "misc"


def infer_dynamic_material_type(tags: List[str], props: Optional[List[str]] = None) -> str:
    """根据 tags/props 推断动态素材类型（禁止 character）。"""
    combined = [str(t).strip().lower() for t in (tags or []) + (props or [])]
    for t in combined:
        norm = t.replace("-", "_")
        if norm in UI_TAG_DIRS or t in UI_TAG_DIRS.values():
            return "ui"
    for t in combined:
        norm = t.replace("-", "_")
        if norm in PROP_TAG_DIRS:
            return "props"
    if any(t in ("effect", "effects", "glow", "blur") for t in combined):
        return "effects"
    return "scene"


def next_sequential_stem(rel_dir: str, prefix: str) -> str:
    """生成 night_office_001 形式 stem。"""
    dir_path = UPLOAD_ROOT / rel_dir
    dir_path.mkdir(parents=True, exist_ok=True)
    pattern = re.compile(rf"^{re.escape(prefix)}_(\d+)$")
    nums: List[int] = []
    for f in dir_path.iterdir():
        if not f.is_file():
            continue
        m = pattern.match(f.stem)
        if m:
            nums.append(int(m.group(1)))
    n = max(nums, default=0) + 1
    return f"{prefix}_{n:03d}"


def build_ai_dynamic_paths(
    *,
    material_type: str,
    scene: str = "office",
    emotion: str = "none",
    tags: Optional[List[str]] = None,
    props: Optional[List[str]] = None,
    ext: str = ".png",
) -> Dict[str, str]:
    """AI 动态素材：顺序命名 night_office_001.png"""
    mtype = _pick_enum(material_type, VALID_TYPES, "scene")
    if mtype == "character":
        raise ValueError("禁止 AI 自动生成角色素材")

    rel_dir = resolve_storage_rel_dir(
        type=mtype,
        role="none",
        emotion=emotion,
        scene=scene,
        tags=tags,
        props=props,
    )

    if mtype == "scene":
        prefix = _pick_enum(scene, VALID_SCENES, "office") or "office"
    elif mtype == "ui":
        prefix = _infer_ui_subdir(tags).replace("-", "_")
    elif mtype == "props":
        prefix = _infer_prop_subdir(tags, props).replace("-", "_")
    else:
        prefix = mtype

    stem = next_sequential_stem(rel_dir, prefix)
    filename = f"{stem}{ext}"
    rel_path = f"{rel_dir}/{filename}"
    return {
        "id": stem,
        "filename": filename,
        "rel_path": rel_path,
        "rel_dir": rel_dir,
        "url": f"{UPLOAD_URL_PREFIX}/{rel_path}",
    }


def build_storage_filename(
    *,
    type: str = "character",
    role: str = "none",
    emotion: str = "none",
    scene: str = "none",
    tags: Optional[List[str]] = None,
    ext: str = ".png",
) -> Tuple[str, str]:
    """
    生成文件名与素材 id（不含扩展名）。
    character: programmer_tired_a83d.png
    """
    suffix = _random_suffix()
    mtype = _pick_enum(type, VALID_TYPES, "character")
    ext = ext if ext.startswith(".") else f".{ext}"

    if mtype == "character":
        role_key = _pick_enum(role, VALID_ROLES, "programmer")
        emotion_key = _pick_enum(emotion, VALID_EMOTIONS, "normal") or "normal"
        if emotion_key == "none":
            emotion_key = "normal"
        stem = f"{role_key}_{emotion_key}_{suffix}"
        return f"{stem}{ext}", stem

    if mtype == "scene":
        scene_key = _pick_enum(scene, VALID_SCENES, "office") or "office"
        if scene_key == "none":
            scene_key = "office"
        stem = f"{scene_key}_{suffix}"
        return f"{stem}{ext}", stem

    if mtype == "ui":
        ui_dir = _infer_ui_subdir(tags)
        ui_key = ui_dir.replace("-", "_")
        stem = f"{ui_key}_{suffix}"
        return f"{stem}{ext}", stem

    if mtype == "props":
        prop_dir = _infer_prop_subdir(tags, props)
        prop_key = prop_dir.replace("-", "_")
        stem = f"{prop_key}_{suffix}"
        return f"{stem}{ext}", stem

    if mtype == "effects":
        stem = f"effect_{suffix}"
        return f"{stem}{ext}", stem

    stem = f"placeholder_{suffix}"
    return f"{stem}{ext}", stem


def build_material_paths(
    *,
    type: str = "character",
    role: str = "none",
    emotion: str = "none",
    scene: str = "none",
    tags: Optional[List[str]] = None,
    ext: str = ".png",
) -> Dict[str, str]:
    """返回 id、相对路径、url、filename。"""
    rel_dir = resolve_storage_rel_dir(
        type=type, role=role, emotion=emotion, scene=scene, tags=tags
    )
    filename, material_id = build_storage_filename(
        type=type, role=role, emotion=emotion, scene=scene, tags=tags, ext=ext
    )
    rel_path = f"{rel_dir}/{filename}"
    url = f"{UPLOAD_URL_PREFIX}/{rel_path}"
    return {
        "id": material_id,
        "filename": filename,
        "rel_path": rel_path,
        "rel_dir": rel_dir,
        "url": url,
    }


def url_to_disk_path(url: str) -> Optional[Path]:
    """将素材 url 解析为磁盘路径；兼容旧版扁平 material_xxx.png。"""
    if not url or not url.strip():
        return None
    raw = url.strip()
    if raw.startswith(UPLOAD_URL_PREFIX):
        rel = raw[len(UPLOAD_URL_PREFIX) + 1 :]
    elif raw.startswith("/uploads/short-drama/"):
        rel = raw[len("/uploads/short-drama/") :]
    else:
        return None
    path = UPLOAD_ROOT / rel
    return path if path.is_file() else None


def ensure_standard_layout() -> None:
    """创建规范目录骨架（已存在则跳过）。"""
    UPLOAD_ROOT.mkdir(parents=True, exist_ok=True)
    for rel in STANDARD_REL_DIRS:
        (UPLOAD_ROOT / rel).mkdir(parents=True, exist_ok=True)


def category_hint(
    *,
    type: str = "character",
    role: str = "none",
    emotion: str = "none",
    scene: str = "none",
) -> Dict[str, str]:
    """供后续随机抽取 / 目录定位使用。"""
    rel_dir = resolve_storage_rel_dir(type=type, role=role, emotion=emotion, scene=scene)
    return {
        "type": _pick_enum(type, VALID_TYPES, "character"),
        "role": _pick_enum(role, VALID_ROLES, ""),
        "emotion": _pick_enum(emotion, VALID_EMOTIONS, ""),
        "scene": _pick_enum(scene, VALID_SCENES, ""),
        "relDir": rel_dir,
        "absDir": str(UPLOAD_ROOT / rel_dir),
    }
