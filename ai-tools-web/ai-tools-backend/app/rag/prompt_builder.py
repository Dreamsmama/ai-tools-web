from __future__ import annotations

from typing import List, Tuple


def build_prompt(query: str, retrieved_chunks: List[dict]) -> Tuple[dict, dict]:
    context_lines = []
    for idx, item in enumerate(retrieved_chunks, start=1):
        context_lines.append(
            f"[{idx}] source={item['filename']} score={item['score']:.4f}\n{item['content']}"
        )
    context_text = "\n\n".join(context_lines)[:7000]

    system = {
        "role": "system",
        "content": (
            "你是知识库问答助手。必须优先使用给定知识库证据回答。"
            "如果证据不足或存在冲突，请明确说明不确定，不要编造。"
        ),
    }
    user = {
        "role": "user",
        "content": (
            f"用户问题：{query}\n\n"
            f"检索证据：\n{context_text}\n\n"
            "请输出：\n"
            "1) 简洁答案\n"
            "2) 关键依据点（可引用证据编号）\n"
            "3) 若证据不足，明确说明缺口。"
        ),
    }
    return system, user
