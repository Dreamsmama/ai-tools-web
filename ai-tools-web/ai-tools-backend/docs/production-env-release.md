# 生产环境变量修改流程（固定）

以后上线统一按这个流程执行。

## 1) 编辑环境变量文件

```bash
vi /root/ai-tools-backend.env
```

示例（新增或修改）：

```env
OPENAI_API_KEY=xxx
RAG_TOP_K=10
```

## 2) 保存退出

在 `vi` 里执行：

```bash
:wq
```

## 3) 重启后端服务（让新变量生效）

> 按你的实际服务名替换 `<backend-service-name>`

```bash
systemctl restart <backend-service-name>
systemctl status <backend-service-name> --no-pager -l
```

---

## 本次「小红书内容生产 Agent」发布：建议变量

```env
# 必填：通义千问 API Key
DASHSCOPE_API_KEY=你的key

# 建议：模型改为 qwen-plus（默认）
DASHSCOPE_MODEL=qwen-plus

# 可选：不填则使用项目默认地址
DASHSCOPE_URL=https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
```

---

## 本次发布可直接执行命令

### A. 按标准流程（vi 手工改）

```bash
vi /root/ai-tools-backend.env
```

把下面三行确认存在（不存在就新增，存在就改成下列值）：

```env
DASHSCOPE_API_KEY=你的key
DASHSCOPE_MODEL=qwen-plus
DASHSCOPE_URL=https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
```

保存退出后重启：

```bash
systemctl restart <backend-service-name>
systemctl status <backend-service-name> --no-pager -l
```

### B. 一把梭（非交互追加/覆盖）

```bash
cat >> /root/ai-tools-backend.env <<'EOF'

# xiaohongshu-agent release
DASHSCOPE_API_KEY=你的key
DASHSCOPE_MODEL=qwen-plus
DASHSCOPE_URL=https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation
EOF
```

然后重启：

```bash
systemctl restart <backend-service-name>
systemctl status <backend-service-name> --no-pager -l
```

