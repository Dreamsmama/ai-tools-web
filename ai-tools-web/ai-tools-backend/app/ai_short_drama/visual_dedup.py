"""
跨 segment 视觉物体去重：同一物体（电脑、会议室、地铁等）在整部视频中只出现一次。

在 enrich_all_segments() 之后、_attach_materials() 之前调用。
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Set, Tuple

logger = logging.getLogger(__name__)

# 视觉物体组：组名 → 触发关键词列表（出现任一即判定为该组）
VISUAL_OBJECT_GROUPS: Dict[str, List[str]] = {
    "computer_screen": ["电脑", "显示器", "屏幕", "VSCode", "终端", "代码", "Bug列表", "bug单", "测试用例", "监控屏"],
    "meeting_room":    ["会议室", "白板", "PPT", "投影幕", "便利贴"],
    "desk":            ["工位", "办公桌", "键盘"],
    "subway":          ["地铁", "车厢", "站台"],
    "convenience_store": ["便利店"],
    "coffee":          ["咖啡"],
    "elevator":        ["电梯"],
    "night_city":      ["城市夜景", "夜景", "城市灯光"],
    "rain_window":     ["雨夜", "窗边雨", "雨天"],
    "phone_msg":       ["手机消息", "飞书红点", "消息红点", "飞书通知"],
    "corridor":        ["楼道", "走廊"],
}

# 职业/办公相关 tag，重写时从 imageTags 中移除
_CAREER_TAGS_TO_REMOVE: frozenset = frozenset({
    "bug", "test_case", "qa", "vscode", "terminal",
    "office_day", "office_night", "night_office",
    "meeting_room", "workstation", "desk",
    "programmer", "tester", "devops", "operations",
})

# 每条备选描述的关键词 → scene key + imageTags
DEDUP_ALTERNATIVE_META: Dict[str, Dict] = {
    "便利店": {
        "scene": "store_night",
        "tags": ["convenience_store", "life_moment", "late_night", "cold_coffee"],
    },
    "地铁末班车": {
        "scene": "subway_night",
        "tags": ["subway_night", "commute", "life_moment", "tired", "daily_life"],
    },
    "楼道窗边": {
        "scene": "corridor_day",
        "tags": ["corridor", "outdoor", "phone_call", "life_moment", "communication"],
    },
    "写字楼附近街道": {
        "scene": "street_night",
        "tags": ["street_night", "commute", "city_night", "life_moment", "cold_coffee"],
    },
    "公司门口路灯": {
        "scene": "street_night",
        "tags": ["street_night", "city_night", "life_moment", "commute"],
    },
    "深夜写字楼楼道": {
        "scene": "corridor_night",
        "tags": ["corridor", "night_light", "life_moment", "tired"],
    },
    "雨夜窗边": {
        "scene": "rainy_window",
        "tags": ["rainy_window", "window_silhouette", "life_moment", "emotion"],
    },
    "下班地铁": {
        "scene": "subway_night",
        "tags": ["subway_night", "commute", "life_moment", "daily_life"],
    },
    "空荡地铁": {
        "scene": "subway_night",
        "tags": ["subway_night", "commute", "life_moment", "daily_life"],
    },
}


def _tags_for_alternative(new_desc: str) -> Tuple[List[str], str]:
    """从备选描述文本推断新的 imageTags 和 scene key。"""
    for keyword, meta in DEDUP_ALTERNATIVE_META.items():
        if keyword in new_desc:
            return meta["tags"], meta["scene"]
    # 兜底：通用生活场景 tag
    return ["life_moment", "commute", "city_night"], "street_night"


# 每个物体组被用掉后的备选场景（按物体组索引），不重复调 API
DEDUP_ALTERNATIVES: Dict[str, List[str]] = {
    "computer_screen": [
        "深夜便利店暖光，货架边低头看手机，外卖袋与纸杯咖啡，治愈又疲惫的打工人瞬间",
        "深夜地铁末班车，空荡车厢，窗外隧道灯光掠过，低头看手机的疲惫背影，耳机线垂落",
        "楼道窗边接电话，城市楼宇背景虚化，手握手机，午后阳光斜射，非会议室内部",
        "写字楼附近街道，路灯下的下班背影，手持纸杯，城市夜色，疲惫通勤感",
    ],
    "meeting_room": [
        "深夜写字楼楼道，走廊灯光，手机来电，疲惫剪影，不是会议室内部",
        "公司门口路灯下，下班人群，手持纸杯咖啡的背影，城市夜色",
        "下班地铁，空荡车厢，窗外城市灯光虚化，一个人的通勤，耳机",
    ],
    "desk": [
        "空荡地铁，窗外城市灯光虚化，耳机，一个人的通勤",
        "深夜便利店暖光，货架边疲惫，手机消息轰炸，打工人凌晨瞬间",
        "雨夜窗边剪影，城市灯光倒映，疲惫安静，工作侵入生活的瞬间",
    ],
    "subway": [
        "深夜便利店暖光，货架边低头看手机，外卖袋与纸杯咖啡",
        "写字楼附近街道，路灯下的下班背影，手持纸杯，城市夜色",
        "雨夜窗边剪影，城市灯光倒映，窗外雨幕，疲惫安静",
    ],
    "convenience_store": [
        "深夜地铁末班车，空荡车厢，窗外隧道灯光掠过，疲惫背影",
        "写字楼附近街道，路灯下的下班背影，手持纸杯，城市夜色",
        "楼道窗边接电话，城市楼宇背景虚化，手握手机，午后阳光斜射",
    ],
    "coffee": [
        "深夜地铁末班车，空荡车厢，窗外城市夜景，低头疲惫背影",
        "楼道窗边，手握手机，城市背景虚化，午后阳光斜射",
        "公司门口路灯下，下班人群，手持外卖袋，城市夜色",
    ],
    "elevator": [
        "深夜地铁末班车，空荡车厢，窗外隧道灯光，低头看手机的疲惫背影",
        "深夜便利店暖光，货架边低头看手机，外卖袋与纸杯咖啡",
        "雨夜窗边剪影，城市灯光倒映，窗外雨幕，一个人的深夜",
    ],
    "night_city": [
        "深夜地铁末班车，空荡车厢，窗外隧道灯光掠过，疲惫背影",
        "深夜便利店暖光，货架边低头看手机，外卖袋与纸杯咖啡",
        "楼道窗边接电话，城市楼宇背景虚化，手握手机，午后阳光斜射",
    ],
    "rain_window": [
        "深夜地铁末班车，空荡车厢，窗外隧道灯光，疲惫背影",
        "深夜便利店暖光，货架边低头看手机，治愈又疲惫的打工人瞬间",
        "写字楼附近街道，路灯下的下班背影，手持纸杯，城市夜色",
    ],
    "phone_msg": [
        "深夜便利店暖光，货架边低头发呆，外卖袋放在脚边，治愈疲惫瞬间",
        "深夜地铁末班车，空荡车厢，窗外隧道灯光，耳机，疲惫背影",
        "雨夜窗边剪影，城市灯光倒映，一个人安静的深夜",
    ],
    "corridor": [
        "深夜地铁末班车，空荡车厢，窗外城市夜景，低头疲惫背影",
        "深夜便利店暖光，货架边低头看手机，外卖袋与纸杯咖啡",
        "写字楼附近街道，路灯下的下班背影，手持纸杯，城市夜色",
    ],
}


def _detect_dominant_group(text: str) -> Optional[str]:
    """从 sceneDescription + imageTags 文本中检测主视觉物体组。返回组名或 None。"""
    if not text:
        return None
    for group, keywords in VISUAL_OBJECT_GROUPS.items():
        for kw in keywords:
            if kw in text:
                return group
    return None


def deduplicate_visual_scenes(segments: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    遍历 segments，检测重复视觉物体组，用备选场景替换重复段落的 sceneDescription。

    重写时同步更新 imageTags 和 scene，确保素材库匹配器不再命中办公室素材，
    转为触发 AI 即梦生图使用新的 sceneDescription。

    规则：
    - 同一物体组在整部视频中最多出现 1 次（第一次出现保留，后续替换）
    - 替换时从 DEDUP_ALTERNATIVES 轮换选取，不重复调用 LLM/API
    - 替换后同步更新 imageTags（移除职业/办公 tag）和 scene key
    """
    used_groups: Set[str] = set()
    alt_counters: Dict[str, int] = {}
    rewritten = 0

    for seg in segments:
        seg_no = seg.get("segmentNo", "?")
        desc = str(seg.get("sceneDescription") or "")
        tags = " ".join(seg.get("imageTags") or [])
        combined = desc + " " + tags

        group = _detect_dominant_group(combined)

        if group and group in used_groups:
            alts = DEDUP_ALTERNATIVES.get(group, [])
            if alts:
                idx = alt_counters.get(group, 0) % len(alts)
                new_desc = alts[idx]
                logger.info(
                    "[visual_dedup] seg=%s group=%s rewrite: %s → %s",
                    seg_no, group, desc[:40], new_desc[:40],
                )
                seg["sceneDescription"] = new_desc
                seg["sceneDescriptionSource"] = "dedup_rewrite"

                # 同步更新 imageTags 和 scene，确保素材匹配器不命中办公室素材
                new_tags, new_scene = _tags_for_alternative(new_desc)
                old_tags = [
                    t for t in (seg.get("imageTags") or [])
                    if t not in _CAREER_TAGS_TO_REMOVE
                ]
                seg["imageTags"] = list(dict.fromkeys(old_tags + new_tags))
                seg["scene"] = new_scene

                alt_counters[group] = idx + 1
                rewritten += 1
        elif group:
            used_groups.add(group)

    if rewritten:
        logger.info("[visual_dedup] total rewritten=%s", rewritten)
    return segments
