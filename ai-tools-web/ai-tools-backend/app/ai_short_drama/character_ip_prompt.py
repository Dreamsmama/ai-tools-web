from __future__ import annotations

import base64
import logging
import mimetypes
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from app.ai_short_drama.character_ip_store import ROLE_LABELS, character_ip_store
from app.ai_short_drama.material_paths import url_to_disk_path
from app.ai_short_drama.profession_store import profession_store
from app.config import settings
from app.utils.llm_json import try_parse_json_object

logger = logging.getLogger(__name__)

CHARACTER_IP_VARIANTS = 4
MAX_REFERENCE_IMAGES = 6

DASHSCOPE_VISION_URL = (
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/multimodal-generation/generation"
)
DASHSCOPE_VISION_MODEL = "qwen-vl-plus"

# 所有角色 IP 生图共享的通用约束
CHARACTER_IP_UNIVERSAL_PREFIX = (
    "【角色IP设定图】竖构图职场短剧动画风，人物设定卡，半写实插画，"
    "简洁纯色或轻渐变背景，人物居中，无文字无水印无logo，"
    "禁止复用其他职业的同款脸型与模板化造型，"
    "每个职业必须是独立可辨认的新人物。"
)

# 四条候选在性别、年龄、发型、服装主色、气质、景别上刻意拉开
VARIANT_ARCHETYPES: List[Dict[str, str]] = [
    {
        "shot": "半身肖像",
        "gender": "男性",
        "age": "27-32岁",
        "hair": "利落短发或寸头",
        "outfit": "深色系卫衣或工装夹克",
        "palette": "冷蓝灰主色",
        "vibe": "内敛专业",
    },
    {
        "shot": "全身立绘",
        "gender": "女性",
        "age": "24-29岁",
        "hair": "中长发或马尾",
        "outfit": "衬衫针织或休闲西装",
        "palette": "暖杏或浅棕主色",
        "vibe": "亲和干练",
    },
    {
        "shot": "半身侧面三分构图",
        "gender": "与候选A性别不同",
        "age": "33-40岁",
        "hair": "偏分或微卷",
        "outfit": "深色西装或风衣",
        "palette": "墨绿或深紫点缀",
        "vibe": "成熟稳重",
    },
    {
        "shot": "正面半身特写",
        "gender": "与候选B性别不同",
        "age": "22-26岁",
        "hair": "有明显辨识度的发型（如挑染、短发层次）",
        "outfit": "亮色点缀的职场休闲（围巾、胸针、背包）",
        "palette": "高对比互补色（避免蓝灰模板）",
        "vibe": "鲜明有个性",
    },
]

CHARACTER_IP_PROMPTS: Dict[str, List[str]] = {
    "programmer": [
        "黑框眼镜短发男性程序员，深灰卫衣，笔记本贴纸，冷蓝背景，技术宅气质",
        "长发女性程序员，连帽衫耳机，暖色台灯氛围，亲和但疲惫",
        "成熟男性后端，格子衬衫挽袖，侧脸三分构图，墨绿暗调",
        "年轻非二元气质程序员，亮色卫衣挑染发，高饱和点缀，个性鲜明",
    ],
    "product_manager": [
        "干练短发女性产品经理，平板与便签，会议室柔光",
        "温和男性产品经理，眼镜针织开衫，浅杏背景",
        "资深女性PM，西装外套，成熟稳重，侧面构图",
        "年轻男性PM，亮色领带点缀，高对比背景，外向气质",
    ],
    "hr": [
        "亲和女性HR，浅色职业装，工牌元素，暖白背景",
        "稳重男性HR，深色西装，面试桌虚化",
        "成熟女性HR总监气质，珍珠耳饰，柔焦背景",
        "年轻男性HR，休闲西装亮色胸针，鲜明构图",
    ],
    "tester": [
        "专注女性测试，耳机bug清单，冷灰工位",
        "戴眼镜男性测试，连帽衫，屏幕反光",
        "资深女性QA，深色上衣，侧面肖像",
        "年轻男性测试，亮色外套，高对比背景",
    ],
    "devops": [
        "深夜值班男性运维，深色工装，服务器指示灯反光",
        "短发女性运维，终端绿光，冷色背景",
        "成熟男性SRE，风衣，侧脸构图",
        "年轻女性运维，亮色安全背心元素，高对比",
    ],
    "sales": [
        "外向女性销售，电话与客户资料，暖色点缀",
        "西装男性销售，自信微笑，浅金背景",
        "资深女性销售总监，深色正装，侧面构图",
        "年轻男性销售，亮色领带，鲜明背景",
    ],
}


@dataclass
class DiversityBrief:
    """生成新角色前，对已有角色图的差异化摘要。"""

    avoidance: str = ""
    tips: List[str] = None  # type: ignore[assignment]
    reference_roles: List[str] = None  # type: ignore[assignment]
    source: str = "none"

    def __post_init__(self) -> None:
        if self.tips is None:
            self.tips = []
        if self.reference_roles is None:
            self.reference_roles = []

    @property
    def prompt_block(self) -> str:
        parts: List[str] = []
        if self.avoidance:
            parts.append(f"【与已有角色区分】{self.avoidance}")
        for i, tip in enumerate(self.tips[:4], 1):
            t = (tip or "").strip()
            if t:
                parts.append(f"【差异化建议{i}】{t}")
        return " ".join(parts)


def _guess_mime(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    return mime or "image/png"


def _image_data_url(path: Path) -> str:
    data = path.read_bytes()
    mime = _guess_mime(path)
    b64 = base64.b64encode(data).decode("ascii")
    return f"data:{mime};base64,{b64}"


def collect_other_active_character_refs(
    exclude_role: str,
    *,
    limit: int = MAX_REFERENCE_IMAGES,
) -> List[Dict[str, Any]]:
    """收集其他职业已启用的角色 IP 图片，供生成前对比。"""
    exclude = exclude_role.strip().lower()
    refs: List[Dict[str, Any]] = []
    for prof in profession_store.list_all():
        role = str(prof.get("roleKey") or "").strip().lower()
        if not role or role == exclude:
            continue
        active = character_ip_store.get_active(role)
        if not active:
            continue
        url = (active.get("baseImageUrl") or "").strip()
        path = url_to_disk_path(url) if url else None
        if not path or not path.is_file():
            continue
        refs.append(
            {
                "role": role,
                "roleLabel": prof.get("name") or ROLE_LABELS.get(role, role),
                "path": path,
                "url": url,
            }
        )
        if len(refs) >= limit:
            break
    return refs


def _rule_based_diversity_brief(
    exclude_role: str,
    refs: List[Dict[str, Any]],
) -> DiversityBrief:
    labels = [str(r.get("roleLabel") or r.get("role") or "") for r in refs]
    labels = [x for x in labels if x]
    if not labels:
        return DiversityBrief(
            avoidance="当前无其他职业角色参考，请确保造型独特、避免模板化网红脸。",
            tips=[
                "四条候选在性别、年龄段、发型、服装主色上至少两项互不相同",
                "避免四张都使用蓝灰冷色与同款半身构图",
            ],
            source="rule_empty",
        )
    joined = "、".join(labels)
    return DiversityBrief(
        avoidance=(
            f"已有职业角色：{joined}。"
            "新职业必须与上述角色在性别、年龄段、发型、服装主色、气质中至少两项明显不同，"
            "禁止同款脸型与模板化造型。"
        ),
        tips=[
            "参考已有图反着设计：若多为女性则候选含男性，若多为冷色则含暖色或高对比色",
            "四条候选之间也要互不相同，不要四张近似换脸",
        ],
        reference_roles=labels,
        source="rule",
    )


async def _call_vision_diversity(messages: List[Dict[str, Any]]) -> str:
    api_key = settings.dashscope_api_key.strip()
    if not api_key:
        raise RuntimeError("缺少 DASHSCOPE_API_KEY")

    payload = {
        "model": DASHSCOPE_VISION_MODEL,
        "input": {"messages": messages},
        "parameters": {"temperature": 0.3, "max_tokens": 900},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    timeout = httpx.Timeout(max(settings.dashscope_timeout_seconds, 60.0))

    async with httpx.AsyncClient(timeout=timeout) as client:
        resp = await client.post(DASHSCOPE_VISION_URL, json=payload, headers=headers)
        resp.raise_for_status()
        body = resp.json()

    content = None
    try:
        choices = body.get("output", {}).get("choices") or []
        if choices:
            msg = choices[0].get("message") or {}
            content = msg.get("content")
        if content is None:
            content = body.get("output", {}).get("text")
    except (TypeError, IndexError, AttributeError):
        content = None

    if isinstance(content, list):
        parts = []
        for part in content:
            if isinstance(part, dict) and part.get("text"):
                parts.append(str(part["text"]))
            elif isinstance(part, str):
                parts.append(part)
        content = "\n".join(parts)

    if not content:
        raise RuntimeError("视觉模型返回为空")
    return content if isinstance(content, str) else str(content)


async def analyze_existing_character_diversity(exclude_role: str) -> DiversityBrief:
    """
    生成新角色前：查看其他职业已选角色图，总结共性并给出差异化约束。
    """
    refs = collect_other_active_character_refs(exclude_role)
    rule_brief = _rule_based_diversity_brief(exclude_role, refs)

    if not refs or not settings.dashscope_api_key.strip():
        logger.info(
            "[角色IP] 差异化分析 refs=%s vision=skipped",
            len(refs),
        )
        return rule_brief

    role_labels = [str(r.get("roleLabel") or "") for r in refs]
    content_parts: List[Any] = []
    for ref in refs:
        try:
            content_parts.append({"image": _image_data_url(ref["path"])})
        except OSError as err:
            logger.warning("[角色IP] 读取参考图失败 %s: %s", ref.get("path"), err)

    if not content_parts:
        return rule_brief

    text_prompt = f"""
你将看到 {len(content_parts)} 张「已有其他职业」的角色 IP 设定图（职业：{'、'.join(role_labels)}）。
请分析这些人物的共同视觉特征，并指导如何为一个【全新职业】生成差异化的新角色。

只返回 JSON，不要 markdown：
{{
  "commonTraits": "一句话概括已有角色的共性（脸型、性别、年龄感、发型、服装、色调、画风）",
  "avoid": "新角色必须避免什么（具体、可执行）",
  "differentiationTips": ["建议1", "建议2", "建议3"]
}}
"""
    content_parts.append({"text": text_prompt.strip()})
    messages = [{"role": "user", "content": content_parts}]

    try:
        raw = await _call_vision_diversity(messages)
        obj = try_parse_json_object(raw) or {}
        avoidance = str(obj.get("avoid") or "").strip()
        common = str(obj.get("commonTraits") or "").strip()
        tips_raw = obj.get("differentiationTips")
        tips: List[str] = []
        if isinstance(tips_raw, list):
            tips = [str(t).strip() for t in tips_raw if str(t).strip()]

        if common and avoidance:
            avoidance = f"已有角色共性：{common}。{avoidance}"

        if avoidance or tips:
            logger.info(
                "[角色IP] 视觉差异化分析完成 refs=%s tips=%s",
                len(refs),
                len(tips),
            )
            return DiversityBrief(
                avoidance=avoidance or rule_brief.avoidance,
                tips=tips or rule_brief.tips,
                reference_roles=role_labels,
                source="vision",
            )
    except Exception as err:
        logger.warning("[角色IP] 视觉差异化分析失败，使用规则兜底: %s", err)

    return rule_brief


def _archetype_clause(arch: Dict[str, str], index: int) -> str:
    return (
        f"【候选{chr(65 + index)}差异化】"
        f"{arch['shot']}，{arch['gender']}，{arch['age']}，"
        f"发型{arch['hair']}，服装{arch['outfit']}，"
        f"主色调{arch['palette']}，气质{arch['vibe']}。"
    )


def _role_trait_clause(role: str, description: str) -> str:
    rk = role.strip().lower()
    label = ROLE_LABELS.get(rk, rk)
    style = (profession_store.style_hint(rk) or "").strip()
    desc = (description or style or "").strip()
    builtins = CHARACTER_IP_PROMPTS.get(rk)
    if builtins and len(builtins) > 0:
        # 内置职业：trait 由索引在 build 时选取
        return desc or label
    if desc:
        return f"{label}职场角色，{desc}"
    return f"{label}职场角色，需体现该职业典型特征但造型独特"


def build_prompts_for_generation(
    role: str,
    description: str = "",
    *,
    diversity: Optional[DiversityBrief] = None,
) -> List[str]:
    """组装 4 条候选 prompt（含通用约束 + 差异化 + 四档造型）。"""
    rk = role.strip().lower()
    label = ROLE_LABELS.get(rk, rk)
    div = diversity or DiversityBrief()
    div_block = div.prompt_block
    trait_base = _role_trait_clause(rk, description)
    builtins = CHARACTER_IP_PROMPTS.get(rk)

    prompts: List[str] = []
    for i in range(CHARACTER_IP_VARIANTS):
        arch = VARIANT_ARCHETYPES[i % len(VARIANT_ARCHETYPES)]
        if builtins and i < len(builtins):
            role_line = f"{label}，{builtins[i]}"
        else:
            role_line = f"{trait_base}，{arch['shot']}"

        prompts.append(
            " ".join(
                [
                    CHARACTER_IP_UNIVERSAL_PREFIX,
                    div_block,
                    _archetype_clause(arch, i),
                    f"【职业特征】{role_line}。",
                    "竖构图1080x1920，无文字水印。",
                ]
            )
        )
    return prompts[:CHARACTER_IP_VARIANTS]
