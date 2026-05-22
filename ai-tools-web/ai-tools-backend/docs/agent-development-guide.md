# Agent 开发规范与技术说明

> 在 ai-tools-backend 中新增或改造 Agent / 多步 LLM 能力时的**通用约定**。  
> 具体业务的 API、存储、环境变量见各模块代码与 [ai-short-drama.md](./ai-short-drama.md)、[production-env-release.md](./production-env-release.md) 等专题文档；**本文不维护改动清单**。

---

## 1. 选型：用哪种形态

| 形态 | 适用场景 | 本仓库示例 |
|------|----------|------------|
| **多步流水线** | 任务可拆成 3～7 个认知步骤，步骤间用结构化数据传递 | `app/agents/xiaohongshu/` + `xiaohongshu_agent_service.py` |
| **领域长 Prompt** | 单步生成，靠强 system 约束画风/合规 | `ai_short_drama/visual_director.py` |
| **RAG** | 答案依赖私有知识库 | `app/rag/qa_service.py` |
| **单步工具** | 一次调用即可，解析可宽松兜底 | `summarize_service.py`、`evening_plan_service.py` |

默认采用 **Python 显式编排**（顺序 `await`），不引入 LangChain / LangGraph，除非出现「步骤顺序由运行时动态决定」的明确需求。

---

## 2. 推荐目录结构（多步 Agent）

```text
app/agents/<agent_name>/
  spec.py              # 步骤顺序、展示标签、Prompt 路径、输出字段绑定
  steps.py             # 各步 run()，只负责调 LLM / 读 Prompt
  prompts/*.md         # 优先 Markdown，用 prompt_loader 加载
  prompt_loader.py     # 可选，与 xiaohongshu 同款即可

app/services/<agent_name>_service.py   # 编排、校验、错误映射、可选 SSE
app/routes/<agent_name>.py             # FastAPI 路由
app/schemas/tools.py                   # Request / Data / Envelope（或独立 schema 模块）
tests/test_<agent_name>.py             # mock LLM，测 JSON 契约与编排
```

**职责划分：**

- `spec.py`：改顺序、加一步、改响应字段映射时**只改这一处**。
- `steps.py`：单步 Prompt 与 `call_dashscope`。
- `*_service.py`：输入校验、循环 `LLM_PIPELINE`、聚合、日志、超时与 `Envelope`。

---

## 3. 步骤间契约：结构化 JSON

- 每步 system/user 明确要求 **只输出 JSON**（在 user 里给字段示例）。
- 步骤之间传 **`dict`**，不要传大段自然语言摘要。
- 解析用 `app/utils/llm_json.try_parse_json_object`；多步 Agent 解析失败应返回明确 `code=500`，避免静默脏数据。
- 最终响应用 Pydantic `Data` + `Envelope`：

```json
{ "code": 0, "data": { ... } }
{ "code": 400, "message": "请先填写..." }
{ "code": 504, "message": "..." }
```

HTTP 可与小程序习惯一致：业务错误仍 200，看 `code`。

---

## 4. LLM 与配置

- 统一走 `app/llm/dashscope_client.call_dashscope`（API Key、model、timeout 一处配置）。
- 长任务（短剧拆段等）在模块内封装更长 timeout，勿拖慢全局默认。
- 环境变量集中在 `app/config/settings.py`；发布前对照 [production-env-release.md](./production-env-release.md)。

---

## 5. Prompt 维护

- 会频繁改的文案 → `prompts/<step>_system.md` / `_user.md`。
- 模板占位用 `load_prompt(name, **vars)`（`str.replace`，避免 `format` 破坏 JSON 花括号）。
- 合规、敏感词等**确定性规则**放 `app/validators/` 或 `app/skills/<name>/code.py`，不要只指望模型。

轻量 Skill 目录约定：`SKILL.md`（给模型的说明）+ 可选 `code.py`（规则引擎），见 `app/skills/content_compliance/`。

---

## 6. 编排、校验与外部能力

**编排器**只做：校验入参 → 按 spec 顺序执行 → 合并字段 → 映射异常到 `user_messages`。

**输出校验**：在 LLM 合并之后用 validator 兜底（空列表、标题长度、敏感词等）。

**Provider**（图 / 视频 / 其它 HTTP 工具）与 LLM 步骤分离：

```python
class ImageProvider:
    async def generate(self, prompts: list[str]) -> list[str]: ...
```

换供应商只改 Provider 实现，不改文案类 Prompt。

**业务硬约束**（职业、角色、禁用词）用 Python 规则在模型输出之后强制覆盖，短剧 `role_catalog` 即此类做法。

---

## 7. 可观测性与长任务

- 每步前后打日志：`step=<id> elapsed=<秒> status=ok|failed`；整请求打 `total=<秒> code=<n>`。
- 单接口总耗时 >20～30s 且步骤固定时，可增加 **SSE**（`text/event-stream`）：
  - `event: progress` → `{ type: step, phase, index, total, label }`
  - `event: result` → 与同步接口相同的 `Envelope` JSON  
  步骤 id 与中文标签与 `spec.py` 共用，避免前后端两套配置。

---

## 8. 测试

- 使用 `unittest` + `patch("app.agents.<name>.steps.call_dashscope", ...)`，固定返回 JSON 字符串。
- 至少覆盖：成功路径、必填校验、JSON 解析失败、空结果、关键 validator 行为。
- 运行：`python3 -m unittest discover -s tests -p 'test_*.py' -v`

---

## 9. 新增 Agent 检查清单

1. [ ] `spec.py` 定义 `LLM_PIPELINE` 与 `RESPONSE_BINDINGS`（或等价结构）
2. [ ] 每步 `run() -> dict`，Prompt 要求 JSON
3. [ ] `*_service.py` 编排，不把所有逻辑塞进一个 Prompt
4. [ ] 路由 + `schemas` + 前端 `api.js` / 页面（若对外暴露）
5. [ ] 复用 `call_dashscope`，不复制 HTTP 客户端
6. [ ] 图/音视频走 Provider 或独立 service
7. [ ] 步骤日志 + 必要时 SSE
8. [ ] mock 单测可离线跑通

---

## 10. 建议避免

- 一个 Prompt 完成分析 + 文案 + 合规（难单步重试、难排障）
- 步骤间用自然语言接力（下一步解析不稳定）
- 每个 service 各自实现 DashScope HTTP
- 为「像框架」引入 LangGraph，而业务仍是固定直线流程
- 每做一次工程优化就新建一篇 changelog 文档（约定写进**本规范**即可）

---

## 11. 本仓库可参考的实现

| 能力 | 路径 |
|------|------|
| 多步 Agent（spec + steps + SSE） | `app/agents/xiaohongshu/`、`app/services/xiaohongshu_agent_service.py` |
| 短剧多段 + 视觉导演 + 即梦 | `app/ai_short_drama/` |
| RAG | `app/rag/qa_service.py` |
| 统一 LLM | `app/llm/dashscope_client.py` |
| JSON 工具 | `app/utils/llm_json.py` |
| 用户可见错误 | `app/utils/user_messages.py` |

前端页面路径见仓库根目录 [PAGES.md](../../PAGES.md)。
