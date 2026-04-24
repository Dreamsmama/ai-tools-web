# AI Tools：面向真实场景的 RAG 智能问答项目

一个可在线访问的 AI 产品化项目，而非“仅调用大模型接口”的演示 Demo。  
项目围绕 **RAG（检索增强生成）** 构建了完整闭环：文档上传 -> 解析清洗 -> 分块向量化 -> 检索召回 -> 引用生成 -> 答案返回，并沉淀查询日志、状态流转和作用域隔离能力。

- 在线访问地址：<http://47.116.6.242>

---

## 1) 项目简介（AI + RAG）

本项目提供两个 AI 能力方向：

1. 通用 AI 工具能力：对话摘要、就诊咨询准备等。
2. RAG 知识问答能力：
   - 支持知识库创建、文档上传与入库；
   - 基于向量检索返回高相关上下文；
   - 生成答案时附带引用片段，提升可解释性；
   - 记录检索/生成/总耗时，便于性能与稳定性分析。

该项目重点体现了一个 AI 功能从“模型调用”到“可运营、可观测、可扩展系统”的工程化落地过程。

---

## 2) 技术栈

### 后端
- Python 3.8+
- FastAPI + Uvicorn
- Pydantic / pydantic-settings（配置与参数校验）
- PostgreSQL + pgvector（结构化数据 + 向量存储）
- psycopg（数据库访问）
- DashScope / 通义（文本生成 + 向量 embedding）

### 前端
- Vue 3 + Vue Router
- Vite

### 部署与网关
- Nginx（`/api` 路由转发到 FastAPI）

---

## 3) 核心功能

- **知识库管理**
  - 创建/列出知识库；
  - 支持官方模板库与用户库可见性控制。
- **文档入库流水线**
  - 文档上传、存储、状态跟踪（`uploaded -> parsing -> parsed -> embedding -> indexed/failed`）；
  - 支持失败重试与错误记录。
- **RAG 问答**
  - Query 规范化、Top-K 约束；
  - 向量检索召回相关 Chunk；
  - 基于检索上下文组装 Prompt 并生成答案；
  - 返回引用来源（文档、chunk、相似度分数）。
- **可观测与追踪**
  - 查询日志落库：检索结果、回答内容、错误信息、trace_id；
  - 关键性能指标：retrieval / generation / total latency。
- **降级与容错**
  - 模型调用失败时，提供基于检索结果的降级答复，保证服务可用性。

### 模型优化实验

- 支持原始模型与优化模型输出对比；
- 当前优化模型为 Prompt 优化占位实现；
- 后续可替换为真实微调模型；
- 用于验证模型优化前后的回答结构化、一致性与可控性差异。
- 新增环境变量：`DASHSCOPE_OPTIMIZED_MODEL`（填微调模型可调用 code；为空时走占位模式）。

---

## 4) 系统架构（文字版）

用户请求先进入前端（Vue），统一经 `/api` 由 Nginx 转发到 FastAPI。  
后端分为两条主链路：

1. **入库链路（离线/准实时）**  
   上传文档 -> 文本解析与清洗 -> Chunk 切分 -> Embedding 生成 -> 写入 pgvector。

2. **问答链路（在线）**  
   用户问题 -> Query 预处理 -> 向量检索（Top-K）-> Prompt 构建 -> LLM 生成 -> 返回答案与引用。

结构化元数据（文档、知识库、日志）与向量数据统一沉淀在 PostgreSQL（含 pgvector），同时通过作用域（user/workspace）做多租户隔离基础。

---

## 5) 项目亮点（工程实践）

### 5.1 不是“裸调模型”，而是完整 RAG 工程闭环
- 有独立的 ingestion pipeline，包含解析、清洗、分块、向量化、入库等步骤；
- 文档状态机 + 失败重试机制，具备生产可用性思维；
- 结果可追溯（引用片段 + query log），可解释性更好。

### 5.2 数据落库设计体现工程能力
- 使用 PostgreSQL 管理知识库、文档、Chunk、查询日志等核心实体；
- 通过 `query_logs` 记录召回 chunk、延迟、trace_id、异常信息，支持后续性能分析与故障排查；
- 通过 `source_type / is_selectable` 管控“官方库发布流程”，体现运营化能力。

### 5.3 向量检索与可扩展边界设计
- 向量存储抽象了 `VectorStore`，默认 `PostgresVectorStore`，预留 `ExternalVectorStore`（Milvus/ES 等）；
- Query Pipeline 预留扩展槽位（query rewrite、hybrid search、rerank、cache、audit），便于演进；
- 预留 ANN 索引优化路径（ivfflat/hnsw），可按数据规模升级检索性能。

### 5.4 服务稳定性与体验兼顾
- 模型不可用时提供降级答案，不让接口直接“硬失败”；
- 接口返回统一 Envelope，前后端对接成本低；
- 通过作用域隔离与默认工作区设计，为后续接入鉴权体系保留演进空间。

---

## 6) 快速启动

> 以下为本地最小可运行流程（后端 + 前端）。

### 6.1 启动后端

```bash
cd ai-tools-web/ai-tools-backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m app.main
```

默认监听：`http://127.0.0.1:8000`

建议先准备：
- 可用 PostgreSQL（开启 pgvector 扩展）；
- DashScope API Key（用于生成与 embedding）。

### 6.2 启动前端

```bash
cd ai-tools-web/ai-tools-frontend
npm install
npm run dev
```

开发模式下由 Vite 代理 API；线上统一通过 `/api` 与 Nginx 对接。

---

## 7) 目录结构优化建议（保持简单，不做过度设计）

当前仓库同时包含小程序与 Web 端能力。建议在不大改代码的前提下做一层分组，提升整体可读性：

```text
miniprogram-2/
  apps/
    web/
      ai-tools-frontend/
      ai-tools-backend/
    miniapp/
      pages/
      cloudfunctions/
      utils/
  docs/
    architecture.md
    api-spec.md
  README.md
```

收益：
- 一眼区分“产品形态”（Web / 小程序）；
- 前后端边界更清晰，便于讲解系统拆分；
- 文档集中沉淀，降低项目协作和维护成本。

---

## 8) 进一步优化建议（后续迭代）

1. **日志与可观测**
   - 引入结构化日志（JSON），统一输出 `trace_id`、`kb_id`、`latency_ms`；
   - 接入 Prometheus 指标（QPS、P95、失败率、检索耗时）。
2. **配置管理**
   - 区分 `dev/staging/prod` 配置，敏感信息走环境变量或密钥管理；
   - 增加配置校验与启动前自检（数据库连通性、关键 env）。
3. **接口规范**
   - 增加 OpenAPI 文档示例与错误码规范；
   - 统一响应码语义（业务错误 vs 系统错误）。
4. **工程质量**
   - 增加单元测试（chunk、retrieval、prompt）和集成测试（上传->入库->问答）；
   - 加入 CI（lint + test + type check）。
5. **RAG 深化**
   - 增加 rerank、hybrid retrieval（BM25 + Vector）；
   - 引入去重召回、上下文压缩、答案置信度评估。

这些优化可进一步提升系统的稳定性、可维护性与可扩展性。
