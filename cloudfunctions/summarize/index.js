/**
 * cloudfunctions/summarize/index.js
 * Node.js 16 compatible
 * 最小可用：qwen-turbo + 2.5s timeout + 严格 JSON
 * 输入：inputText
 * 输出：{ code:0, data:{ summary,todos,risks,reply } }
 */

const axios = require("axios");

function safeTrim(v) {
  return typeof v === "string" ? v.trim() : "";
}

async function callDashScopeFast(messages) {
  const apiKey = process.env.DASHSCOPE_API_KEY;
  if (!apiKey) throw new Error("缺少 DASHSCOPE_API_KEY 环境变量");

  const url =
    "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation";

  const resp = await axios.post(
    url,
    {
      model: "qwen-turbo",
      input: { messages },
      parameters: {
        temperature: 0.2,
        max_tokens: 512
      }
    },
    {
      headers: {
        Authorization: `Bearer ${apiKey}`,
        "Content-Type": "application/json"
      },
      timeout: 2500
    }
  );

  const json = resp.data;

  const content =
    json?.output?.choices?.[0]?.message?.content ??
    json?.output?.text ??
    json?.output?.choices?.[0]?.text;

  if (!content) {
    throw new Error(
      "DashScope 返回为空或结构不匹配：" + JSON.stringify(json).slice(0, 500)
    );
  }

  return content;
}

function parseStrictJson(content) {
  let obj;
  try {
    obj = JSON.parse(content);
  } catch (e) {
    // 兜底：截取第一个 { 到最后一个 }
    const s = content.indexOf("{");
    const e2 = content.lastIndexOf("}");
    if (s >= 0 && e2 > s) {
      obj = JSON.parse(content.slice(s, e2 + 1));
    } else {
      throw new Error("模型返回非JSON");
    }
  }

  const summary = Array.isArray(obj.summary) ? obj.summary : [];
  const todos = Array.isArray(obj.todos) ? obj.todos : [];
  const risks = Array.isArray(obj.risks) ? obj.risks : [];
  const reply = typeof obj.reply === "string" ? obj.reply : "";

  // todos 每项应该是 {owner,task,due}
  const normTodos = todos
    .map((t) => ({
      owner: typeof t?.owner === "string" ? t.owner : "未明确",
      task: typeof t?.task === "string" ? t.task : String(t || ""),
      due: typeof t?.due === "string" ? t.due : ""
    }))
    .filter((t) => t.task && t.task.trim())
    .slice(0, 6);

  return {
    summary: summary.map(String).slice(0, 5),
    todos: normTodos,
    risks: risks.map(String).slice(0, 5),
    reply: reply.trim()
  };
}

exports.main = async (event) => {
  try {
    const inputText = safeTrim(event.inputText);

    if (!inputText) {
      return { code: 400, message: "inputText 不能为空" };
    }

    const systemMessage = {
      role: "system",
      content:
        "你是“聊天重点总结器”。只做信息提炼与行动整理，不编造事实。" +
        "只输出严格 JSON，不要 markdown，不要多余文本。"
    };

    const userMessage = {
      role: "user",
      content: `
请把下面聊天内容整理为严格 JSON（不要markdown、不要多余文本）：
{
  "summary": ["...","...","..."],
  "todos": [{"owner":"我/对方/未明确","task":"...","due":""}],
  "risks": ["...","..."],
  "reply": "一段可直接复制发送的确认话术"
}

规则：
- summary：3~5条，短句，提炼结论/共识/决定
- todos：2~6条，能执行的动作，owner 尽量判断（我/对方/未明确），due 没有就空字符串
- risks：2~5条，没说清/容易扯皮/需要确认的点
- reply：1段，可直接发群/私聊的确认话术（简洁、不强势）

聊天内容：
${inputText}
`.trim()
    };

    const content = await callDashScopeFast([systemMessage, userMessage]);

    const data = parseStrictJson(content);

    // 最小兜底：避免前端直接挂
    if (!data.summary.length && !data.todos.length && !data.risks.length && !data.reply) {
      return { code: 500, message: "模型输出为空/不符合格式" };
    }

    // reply 太长就截断一下（避免 max_tokens 波动）
    if (data.reply && data.reply.length > 400) {
      data.reply = data.reply.slice(0, 400);
    }

    return { code: 0, data };
  } catch (err) {
    console.error("summarize error:", err?.message || err);

    if (String(err?.message || "").includes("timeout")) {
      return { code: 504, message: "生成超时，请重试（网络或模型响应较慢）" };
    }

    return { code: 500, message: err?.message || "server error" };
  }
};



