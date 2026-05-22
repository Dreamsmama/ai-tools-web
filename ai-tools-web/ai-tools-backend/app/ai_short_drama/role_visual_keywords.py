"""
职业视觉关键词：每个职业独立的视觉宇宙，避免全片「会议室+电脑+工位」。
"""

from __future__ import annotations

import re
from typing import Any, Dict, FrozenSet, List, Optional

from app.ai_short_drama.scene_intent import GENERIC_OFFICE_SCENES, SceneIntent

# 素材匹配 / 生图用的 canonical 职业键（与 roleKey 可不同，见 VISUAL_ROLE_ALIASES）
VISUAL_ROLES = frozenset(
    {
        "programmer",
        "designer",
        "product_manager",
        "hr",
        "admin",
        "operations",
        "tester",
        "devops",
        "sales",
    }
)

ROLE_VISUAL_KEYWORDS: Dict[str, List[str]] = {
    "programmer": [
        "VSCode",
        "Linux终端",
        "Git",
        "红色报错",
        "深夜工位",
        "双显示器",
        "API",
        "日志",
        "服务器监控",
        "工单",
        "Jira",
    ],
    "designer": [
        "Figma",
        "UI设计稿",
        "调色板",
        "字体",
        "MacBook",
        "iPad",
        "灵感墙",
        "海报",
        "视觉稿",
        "色卡",
        "草图",
        "改稿",
        "设计评审",
    ],
    "product_manager": [
        "PRD",
        "流程图",
        "Axure",
        "白板",
        "需求评审",
        "PPT",
        "飞书",
        "Jira",
        "排期表",
        "用户故事",
    ],
    "hr": [
        "简历",
        "面试间",
        "招聘后台",
        "候选人消息",
        "Excel",
        "微信沟通",
        "Offer",
        "背调",
    ],
    "admin": [
        "前台",
        "办公文件",
        "会议安排",
        "Excel",
        "访客登记",
        "办公室走廊",
        "工牌",
        "资料夹",
    ],
    "operations": [
        "数据后台",
        "活动页",
        "Excel",
        "用户增长图",
        "社群消息",
        "直播数据",
        "投放素材",
        "转化漏斗",
    ],
    "tester": [
        "Bug单",
        "测试用例",
        "复现步骤",
        "测试环境",
        "回归",
        "缺陷列表",
    ],
    "devops": [
        "监控大屏",
        "告警",
        "终端",
        "部署",
        "日志",
        "服务器",
        "oncall",
    ],
    "sales": [
        "客户微信",
        "电话",
        "CRM",
        "业绩表",
        "合同",
        "出差",
    ],
}

# roleKey / 中文职业名 → 视觉职业键
VISUAL_ROLE_ALIASES: Dict[str, str] = {
    "ui": "designer",
    "ux": "designer",
    "prof_cbb78e8a": "designer",
    "前端开发": "programmer",
    "prof_5338258d": "programmer",
    "猎头": "hr",
    "prof_09b95b5ca1": "hr",
    "行政": "admin",
    "prof_795c7abc": "admin",
}

ROLE_CN_TO_VISUAL: Dict[str, str] = {
    "程序员": "programmer",
    "设计师": "designer",
    "ui设计师": "designer",
    "UI设计师": "designer",
    "UI设计": "designer",
    "视觉设计": "designer",
    "产品经理": "product_manager",
    "产品": "product_manager",
    "HR": "hr",
    "hr": "hr",
    "人事": "hr",
    "测试": "tester",
    "运维": "devops",
    "运营": "operations",
    "销售": "sales",
    "行政": "admin",
    "前台": "admin",
}

# 英文 tag slug（素材匹配 / imageTags）
ROLE_VISUAL_TAG_SLUGS: Dict[str, List[str]] = {
    "programmer": [
        "vscode",
        "terminal",
        "git",
        "error_log",
        "dual_monitor",
        "api",
        "jira",
        "oncall",
    ],
    "designer": [
        "figma",
        "ui_design",
        "color_palette",
        "typography",
        "macbook",
        "ipad",
        "moodboard",
        "poster",
        "sketch",
        "revision",
    ],
    "product_manager": [
        "prd",
        "flowchart",
        "axure",
        "whiteboard",
        "feishu",
        "jira",
        "ppt",
    ],
    "hr": [
        "resume",
        "interview",
        "excel",
        "wechat",
        "candidate",
        "recruitment",
    ],
    "admin": [
        "reception",
        "office_files",
        "meeting_schedule",
        "excel",
        "visitor_log",
        "corridor",
        "badge",
        "folder",
    ],
    "operations": [
        "dashboard",
        "campaign",
        "growth_chart",
        "community",
        "live_data",
    ],
    "tester": ["bug", "test_case", "qa"],
    "devops": ["monitoring", "alert", "deploy", "server_room"],
    "sales": ["crm", "phone_call", "contract"],
}

# 非该职业时应降权的 scene_key（避免设计师片全是工位）
ROLE_PENALIZE_SCENES: Dict[str, FrozenSet[str]] = {
    "designer": frozenset(
        {"desk", "workstation", "server_room", "meeting_room", "workstation"}
    ),
    "product_manager": frozenset({"server_room", "workstation"}),
    "hr": frozenset({"server_room", "desk", "workstation"}),
    "operations": frozenset({"server_room", "interview_room"}),
    "sales": frozenset({"server_room", "desk"}),
    "admin": frozenset({"desk", "workstation", "server_room", "meeting_room"}),
    "programmer": frozenset({"interview_room"}),
}

# 各职业在 sceneIntent 下的默认生图描述（覆盖通用「会议室/工位」模板）
ROLE_INTENT_GENERATION: Dict[str, Dict[str, Dict[str, str]]] = {
    "designer": {
        "opening": {
            "scene": "竖屏设计师工作室晨光，灵感墙与色卡，MacBook与iPad，无人正脸，9:16留白",
            "ui": "竖屏Figma空白画板，清晨柔和界面",
            "scene_key": "office_day",
        },
        "communication": {
            "scene": "竖屏设计评审白板，便利贴与线框草图，非程序员工位大特写",
            "ui": "竖屏Figma评论与@批注列表，改稿讨论",
            "scene_key": "meeting_room",
        },
        "work_pressure": {
            "scene": "竖屏深夜设计工作台，Figma满屏改稿标注，冷咖啡，压迫感",
            "ui": "竖屏Figma版本对比与红色批注层",
            "scene_key": "night_office",
        },
        "fatigue": {
            "scene": "竖屏设计师趴桌小憩，色卡散落，显示器Figma虚化，疲惫安静",
            "ui": "竖屏设计稿图层过多列表，未读评论",
            "scene_key": "night_office",
        },
        "collapse": {
            "scene": "竖屏改稿截止，屏幕上满屏红色修改意见，设计师双手抱头剪影",
            "ui": "竖屏「第12版」设计稿文件名与批注轰炸",
            "scene_key": "night_office",
        },
        "emotion": {
            "scene": "竖屏窗边设计师背影，城市夜景，画板草图与色卡，情绪留白",
            "effects": "竖屏渐暗蓝调，海报草稿虚化",
            "scene_key": "office_night",
        },
        "daily_life": {
            "scene": "竖屏地铁通勤背包里露出iPad与速写本，设计师下班路上",
            "props": "竖屏便利店咖啡与速写本",
            "scene_key": "office_day",
        },
    },
    "product_manager": {
        "opening": {
            "scene": "竖屏产品会议室白板流程图，便利贴用户故事，非工位壁纸",
            "ui": "竖屏Axure或白板原型线框",
            "scene_key": "meeting_room",
        },
        "work_pressure": {
            "scene": "竖屏PRD文档与排期表堆叠，飞书未读，深夜会议室",
            "ui": "竖屏Jira需求池与优先级标红",
            "scene_key": "night_office",
        },
        "communication": {
            "scene": "竖屏跨部门评审，投影需求文档一角",
            "ui": "竖屏飞书文档协作光标",
            "scene_key": "meeting_room",
        },
    },
    "hr": {
        "opening": {
            "scene": "竖屏HR工位简历堆与日历，柔和办公灯，非程序员显示器代码",
            "ui": "竖屏招聘系统候选人列表",
            "scene_key": "office_day",
        },
        "communication": {
            "scene": "竖屏面试间圆桌，简历文件夹，礼貌距离构图",
            "ui": "竖屏微信面试邀约聊天",
            "scene_key": "interview_room",
        },
        "work_pressure": {
            "scene": "竖屏深夜HR整理Excel排期，多屏招聘数据",
            "ui": "竖屏招聘后台待处理红点",
            "scene_key": "night_office",
        },
    },
    "operations": {
        "opening": {
            "scene": "竖屏运营数据分析大屏，增长曲线，活动banner草稿",
            "ui": "竖屏活动页后台配置界面",
            "scene_key": "office_day",
        },
        "work_pressure": {
            "scene": "竖屏活动上线倒计时，数据仪表盘告警黄灯",
            "ui": "竖屏社群消息刷屏与数据下跌",
            "scene_key": "night_office",
        },
    },
}

# 设计师等职业：LLM 写出这些词且无职业关键词 → 视为无效模板
ROLE_GENERIC_MARKERS: Dict[str, tuple[str, ...]] = {
    "designer": ("会议室", "工位", "VSCode", "Jira", "Git", "Linux", "报错", "双显示器"),
    "product_manager": ("VSCode", "Git", "Linux终端", "红色报错", "服务器"),
    "hr": ("VSCode", "Git", "Figma", "代码", "报错"),
    "operations": ("VSCode", "Git", "Figma", "面试间"),
    "admin": ("VSCode", "Git", "代码", "显示器", "Jira", "报错"),
    "programmer": (),  # 使用 visual_director 默认
}


def resolve_visual_role_key(role_key: str = "", career_cn: str = "") -> str:
    """将 roleKey / 中文职业解析为视觉职业键。"""
    cn = (career_cn or "").strip()
    if cn:
        if cn in ROLE_CN_TO_VISUAL:
            return ROLE_CN_TO_VISUAL[cn]
        low = cn.lower()
        for name, visual in ROLE_CN_TO_VISUAL.items():
            if name.lower() in low or low in name.lower():
                return visual
        if "设计" in cn:
            return "designer"
        if "产品" in cn:
            return "product_manager"
        if "运营" in cn:
            return "operations"

    rk = (role_key or "").strip().lower()
    if rk in ROLE_VISUAL_KEYWORDS:
        return rk
    if rk in VISUAL_ROLE_ALIASES:
        return VISUAL_ROLE_ALIASES[rk]
    if rk in ROLE_CN_TO_VISUAL:
        return ROLE_CN_TO_VISUAL[rk]
    return "programmer"


def get_role_visual_keywords(visual_role: str) -> List[str]:
    key = resolve_visual_role_key(visual_role)
    return list(ROLE_VISUAL_KEYWORDS.get(key, ROLE_VISUAL_KEYWORDS["programmer"]))


def role_visual_tag_slugs(visual_role: str) -> List[str]:
    key = resolve_visual_role_key(visual_role)
    return list(ROLE_VISUAL_TAG_SLUGS.get(key, []))


def role_penalized_scenes(visual_role: str) -> FrozenSet[str]:
    key = resolve_visual_role_key(visual_role)
    return ROLE_PENALIZE_SCENES.get(key, frozenset())


def role_visual_keywords_cn(visual_role: str, *, limit: int = 6) -> str:
    kws = get_role_visual_keywords(visual_role)[:limit]
    return "，".join(kws) if kws else ""


def prompt_role_visual_block(role_key: str = "", career_cn: str = "") -> str:
    """注入 LLM system：职业点缀 + 生活感（非职业科普）。"""
    from app.ai_short_drama.life_moment_visual import prompt_life_moment_block

    visual = resolve_visual_role_key(role_key, career_cn)
    kws = role_visual_keywords_cn(visual, limit=5)
    if not kws:
        return prompt_life_moment_block()
    label = career_cn or visual
    forbidden = _forbidden_hint_for_role(visual)
    return (
        f"\n【{label} · 职业点缀】画面可轻量出现（虚化/一角，勿占满）：{kws}。"
        f"须与生活碎片组合，禁止做成职业介绍PPT。"
        f"{forbidden}"
        f"{prompt_life_moment_block()}"
    )


def _forbidden_hint_for_role(visual: str) -> str:
    base = "禁止职业科普句式、禁止软件界面占满全屏、禁止「在办公室做XX」。"
    if visual == "designer":
        return base + "不要永远Figma大图；要有改稿到凌晨、耳机、雨夜、凌乱桌面。"
    if visual == "product_manager":
        return base + "不要永远PRD+会议室；要有电梯回消息、深夜飞书、下班地铁。"
    if visual == "hr":
        return base + "不要写代码工位；要有简历、面试、微信约面与生活感。"
    if visual == "operations":
        return base + "不要开发工位；要有数据屏一角+深夜便利店/通勤。"
    if visual == "admin":
        return base + "不要程序员代码场景；优先前台/文件/访客登记/走廊/工牌。"
    return base + "禁止空泛「会议室+电脑+工位」套模板。"


def is_generic_scene_for_role(desc: str, role_key: str = "", career_cn: str = "") -> bool:
    """职业语境下的空泛 sceneDescription。"""
    t = (desc or "").strip()
    if len(t) < 8:
        return True
    visual = resolve_visual_role_key(role_key, career_cn)
    markers = ROLE_GENERIC_MARKERS.get(visual)
    if markers:
        hits = sum(1 for m in markers if m in t)
        kw_hits = sum(1 for k in get_role_visual_keywords(visual) if k in t)
        if hits >= 1 and kw_hits == 0:
            return True
        if hits >= 2:
            return True
    from app.ai_short_drama.life_moment_visual import is_career_ppt_description
    from app.ai_short_drama.visual_director import is_generic_scene_description

    if is_career_ppt_description(t):
        return True
    return is_generic_scene_description(t)


def inject_role_keywords_into_desc(
    desc: str,
    visual_role: str,
    *,
    intent: str = "emotion",
    text: str = "",
    segment_no: int = 1,
    emotion: str = "",
) -> str:
    from app.ai_short_drama.life_moment_visual import compose_cinematic_moment

    return compose_cinematic_moment(
        desc,
        visual_role=visual_role,
        intent=intent,
        text=text,
        segment_no=segment_no,
        emotion=emotion,
    )


def merge_role_intent_generation(
    plan: Dict[str, Any],
    visual_role: str,
    intent: str,
    text: str = "",
    *,
    segment_no: int = 1,
    emotion: str = "",
) -> Dict[str, Any]:
    """职业镜头 + 生活碎片 → 电影感瞬间（非职业 PPT）。"""
    from app.ai_short_drama.life_moment_visual import blend_life_into_plan

    role_overrides = ROLE_INTENT_GENERATION.get(visual_role, {}).get(intent)
    if role_overrides:
        gen = dict(plan.get("generation") or {})
        for mtype in ("scene", "ui", "effects", "props"):
            if role_overrides.get(mtype):
                gen[mtype] = str(role_overrides[mtype])
        sk = role_overrides.get("scene_key")
        if sk:
            plan["sceneKey"] = sk
        plan["generation"] = gen
        hints = list(plan.get("sceneHints") or [])
        for slug in role_visual_tag_slugs(visual_role)[:4]:
            if slug not in hints:
                hints.append(slug)
        plan["sceneHints"] = hints

    plan["visualRole"] = visual_role
    return blend_life_into_plan(
        plan,
        visual_role,
        intent,
        text,
        segment_no=segment_no,
        emotion=emotion,
    )


def append_role_visual_tags(tags: List[str], role_key: str = "", career_cn: str = "") -> List[str]:
    visual = resolve_visual_role_key(role_key, career_cn)
    out = [str(t).strip().lower() for t in tags if str(t).strip()]
    if visual not in out:
        out.insert(0, visual)
    for slug in role_visual_tag_slugs(visual):
        if slug not in out:
            out.append(slug)
    penalized = role_penalized_scenes(visual)
    if visual != "programmer":
        out = [t for t in out if t not in GENERIC_OFFICE_SCENES or t not in penalized]
    return out[:16]


def infer_visual_role_from_text(text: str) -> str:
    t = (text or "").strip()
    if not t:
        return ""
    if re.search(r"设计|Figma|UI|视觉|改稿|色卡|海报", t, re.I):
        return "designer"
    if re.search(r"产品|PRD|需求|排期|Axure", t, re.I):
        return "product_manager"
    if re.search(r"招聘|面试|简历|候选人|HR", t, re.I):
        return "hr"
    if re.search(r"运营|活动|增长|转化|社群|投放", t):
        return "operations"
    if re.search(r"代码|上线|报错|Git|VSCode|接口|部署", t, re.I):
        return "programmer"
    return ""
