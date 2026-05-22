from __future__ import annotations

from typing import Any, Dict, List, Optional

DEFAULT_MATERIAL_URL = ""

MATERIAL_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "programmer_tired_001",
        "name": "疲惫程序员",
        "url": "/short-drama/programmer_tired_001.png",
        "tags": ["programmer", "tired", "night_office"],
    },
    {
        "id": "programmer_error_001",
        "name": "报错日志屏",
        "url": "/short-drama/programmer_error_001.png",
        "tags": ["programmer", "error_log", "night_office"],
    },
    {
        "id": "programmer_hoodie_001",
        "name": "灰色卫衣工位",
        "url": "/short-drama/programmer_hoodie_001.png",
        "tags": ["programmer", "hoodie", "office"],
    },
    {
        "id": "pm_meeting_001",
        "name": "产品经理开会",
        "url": "/short-drama/pm_meeting_001.png",
        "tags": ["product_manager", "meeting", "confident"],
    },
    {
        "id": "pm_laptop_001",
        "name": "拿电脑的 PM",
        "url": "/short-drama/pm_laptop_001.png",
        "tags": ["product_manager", "laptop", "office"],
    },
    {
        "id": "hr_interview_001",
        "name": "HR 面试现场",
        "url": "/short-drama/hr_interview_001.png",
        "tags": ["hr", "interview", "resume"],
    },
    {
        "id": "hr_messages_001",
        "name": "飞书消息轰炸",
        "url": "/short-drama/hr_messages_001.png",
        "tags": ["hr", "messages", "office"],
    },
    {
        "id": "tester_bug_001",
        "name": "测试背锅现场",
        "url": "/short-drama/tester_bug_001.png",
        "tags": ["tester", "bug", "blame"],
    },
    {
        "id": "ops_alert_001",
        "name": "凌晨报警",
        "url": "/short-drama/ops_alert_001.png",
        "tags": ["ops", "alert", "night", "oncall"],
    },
    {
        "id": "sales_phone_001",
        "name": "销售电话跟进",
        "url": "/short-drama/sales_phone_001.png",
        "tags": ["sales", "phone", "pressure"],
    },
    {
        "id": "office_night_001",
        "name": "深夜办公室",
        "url": "/short-drama/office_night_001.png",
        "tags": ["night_office", "office", "late"],
    },
    {
        "id": "meeting_room_001",
        "name": "会议室",
        "url": "/short-drama/meeting_room_001.png",
        "tags": ["meeting", "office"],
    },
]

CAREER_TAG_HINTS: Dict[str, List[str]] = {
    "程序员": ["programmer", "tired", "night_office", "error_log"],
    "产品经理": ["product_manager", "meeting", "confident"],
    "HR": ["hr", "interview", "resume"],
    "测试": ["tester", "bug"],
    "运维": ["ops", "alert", "oncall"],
    "销售": ["sales", "phone"],
}


def get_default_material() -> Dict[str, Any]:
    return {
        "id": "material_missing",
        "name": "缺少可用素材",
        "url": "",
        "tags": [],
    }


def match_material(image_tags: List[str]) -> Dict[str, Any]:
    """保留旧接口；实际逻辑见 material_matcher。"""
    from app.ai_short_drama.material_matcher import match_material as _match

    return _match(image_tags)
