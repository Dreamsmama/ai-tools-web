# 阿里云微调与项目接入指南

本文面向当前项目的「模型优化实验 / 微调效果对比」功能，目标是：

1. 在阿里云百炼（DashScope）完成 SFT 微调；
2. 将微调后的模型接到项目 `optimized_output`；
3. 保持 `original_output` 继续走原始基座模型，便于对比。

---

## 1. 准备训练数据

本项目已提供样例文件：

- `docs/fine-tune-sft-data.sample.jsonl`

你可以先用它跑通流程，再扩充到 200+ 条高质量样本。

数据格式（每行一条 JSON）：

```json
{"messages":[
  {"role":"system","content":"系统指令"},
  {"role":"user","content":"用户输入"},
  {"role":"assistant","content":"期望输出"}
]}
```

建议：

- 期望输出保持稳定结构：`【核心问题】`、`【分析】`、`【建议】`
- 避免互相冲突样本
- 优先覆盖你真实业务场景输入

---

## 2. 在阿里云百炼创建微调任务（SFT）

1) 登录阿里云百炼控制台，进入模型调优（Fine-tune）。  
2) 上传 `jsonl` 训练集文件。  
3) 选择基座模型（建议和线上原始模型同家族，便于对比）。  
4) 训练类型选择 `SFT`。  
5) 设置超参数（建议首版）：

- `n_epochs`: 1~2
- `split`: 0.9
- `learning_rate`: 保守小值起步

6) 提交训练并等待完成。  
7) 记录训练产出的 **微调模型名称/ID**（后续写入环境变量）。

---

## 3. 用 API 方式（可选）

如果你习惯 API，可按 DashScope 文档进行：

- 上传文件，拿到 `file_id`
- 调用 `/api/v1/fine-tunes` 创建 SFT 任务
- 轮询任务状态
- 获取训练后模型名

说明：控制台更省事，建议先控制台跑通第一版。

---

## 4. 项目中如何替换为微调模型

本项目已做可切换改造，你只需要改 `.env`：

```env
DASHSCOPE_MODEL=qwen-turbo
DASHSCOPE_OPTIMIZED_MODEL=<你的微调模型名或ID>
```

规则：

- `original_output` 继续使用 `DASHSCOPE_MODEL`
- `optimized_output` 优先使用 `DASHSCOPE_OPTIMIZED_MODEL`
- 若 `DASHSCOPE_OPTIMIZED_MODEL` 为空，则自动回退到 Prompt 占位模式

相关代码位置：

- 配置项：`app/config.py`
- 对比逻辑：`app/model_compare_service.py`
- 通用调用：`app/summarize_service.py`

---

## 5. 启动与验证

1) 修改 `.env` 后重启后端。  
2) 打开前端「模型优化实验 / 微调效果对比」页面。  
3) 用页面内示例输入做对比，观察：

- 结构命中率（是否稳定输出三段）
- 一致性（风格是否稳定）
- 可控性（是否减少跑题）

接口返回的 `mode`：

- `placeholder`：仍是 Prompt 占位
- `fine_tuned`：已切换到微调模型

---

## 6. 常见问题排查

- 返回 401/403：检查 `DASHSCOPE_API_KEY`
- 返回模型不存在：确认 `DASHSCOPE_OPTIMIZED_MODEL` 填的是训练后可调用模型名
- 优化结果看不出差异：扩充训练数据覆盖面，并增加高质量“反例场景”
- 结构仍偶发不稳定：在训练集中提高结构化输出样本占比
