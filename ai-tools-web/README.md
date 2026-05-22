# ai-tools-web

Web 版 AI 工具集（Vue 3 + Vite 前端，FastAPI 后端）。

## 本地开发

```bash
# 终端 1 — 后端
cd ai-tools-backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # 填写 DASHSCOPE_API_KEY、JIMENG_API_KEY 等
python -m app.main     # http://127.0.0.1:8000

# 终端 2 — 前端
cd ai-tools-frontend
npm install
npm run dev            # http://127.0.0.1:5173
```

## 文档

| 文档 | 说明 |
|------|------|
| **[PAGES.md](./PAGES.md)** | 页面入口路径（本地 / 生产） |
| **[ai-tools-backend/docs/agent-development-guide.md](./ai-tools-backend/docs/agent-development-guide.md)** | **Agent 开发规范**（后期扩展多步 Agent 时参考） |
| [ai-tools-backend/docs/README.md](./ai-tools-backend/docs/README.md) | 后端文档索引 |
| [ai-short-drama.md](./ai-tools-backend/docs/ai-short-drama.md) | AI 短剧技术说明 |
