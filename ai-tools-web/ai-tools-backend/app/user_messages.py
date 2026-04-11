"""
返回给前端的说明：偏「可立即再试」话术；配置/网关类仍保留找管理员的提示。
"""

from __future__ import annotations

# 通用：鼓励直接重试，不改输入
_RETRY_SOFT = (
    "无需修改已填写的内容，直接再点一次提交即可；"
    "大模型偶尔不稳定，通常重试 1～2 次就会好。"
)


def msg_input_empty() -> str:
    return "请先粘贴或填写内容，再点提交。"


def msg_timeout() -> str:
    return (
        "本次等待超时，多半是网络或模型响应稍慢。\n"
        + _RETRY_SOFT
    )


def msg_model_empty() -> str:
    return (
        "本次没有生成出可用结果。\n"
        + _RETRY_SOFT
    )


def msg_api_key_missing() -> str:
    return (
        "服务未正确配置大模型密钥，需要管理员在服务器上设置环境变量后重启。\n"
        "个人用户侧反复点击无法解决，请联系管理员。"
    )


def msg_upstream_error() -> str:
    return (
        "大模型服务暂时异常（如限流、欠费或接口波动）。\n"
        + _RETRY_SOFT
        + "\n若多次重试仍失败，再联系管理员。"
    )


def msg_generic_server() -> str:
    return (
        "服务暂时未完成本次请求。\n"
        + _RETRY_SOFT
        + "\n若连续多次失败，再联系管理员。"
    )


def from_exception(err: BaseException) -> str:
    """把内部异常转成用户可读说明（详细错误仍写在 logger 里）。"""
    raw = str(err) if err else ""
    low = raw.lower()

    if "DASHSCOPE_API_KEY" in raw or ("缺少" in raw and "api" in low and "key" in low):
        return msg_api_key_missing()
    if "timeout" in low:
        return msg_timeout()
    if "dashscope" in low or "401" in raw or "403" in raw:
        return msg_upstream_error()
    if "返回为空" in raw or "结构不匹配" in raw:
        return msg_upstream_error()

    return msg_generic_server()
