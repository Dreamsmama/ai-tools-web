/**
 * cloudfunctions/prepareConsult/index.js
 * Node.js 16 compatible
 * 方案3：应急压缩（尽量 < 3s）：
 * - 模型：qwen-turbo
 * - max_tokens：256
 * - axios timeout：2500ms（云函数3s限制下提前掐断）
 * - 输出固定为短JSON：summary(3) / questions(3) / notes(2)
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
        max_tokens: 256
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
    const s = content.indexOf("{");
    const e2 = content.lastIndexOf("}");
    if (s >= 0 && e2 > s) {
      obj = JSON.parse(content.slice(s, e2 + 1));
    } else {
      throw new Error("模型返回非JSON");
    }
  }

  const summary = Array.isArray(obj.summary) ? obj.summary : [];
  const questions = Array.isArray(obj.questions) ? obj.questions : [];
  const notes = Array.isArray(obj.notes) ? obj.notes : [];

  return {
    summary: summary.map(String).slice(0, 3),
    questions: questions.map(String).slice(0, 3),
    notes: notes.map(String).slice(0, 2)
  };
}

exports.main = async (event, context) => {
  try {
    const symptom = safeTrim(event.symptom);
    const report = safeTrim(event.report);
    const target = safeTrim(event.target);

    if (!symptom) {
      return { code: 400, message: "symptom 不能为空" };
    }

    const systemMessage = {
      role: "system",
      content:
        "你是“就医前问诊准备助手”。严格禁止：诊断、治疗/用药建议、判断严重程度。" +
        "只做：信息整理、提问准备、注意点提醒（中性）。" +
        "只输出严格 JSON，不要 markdown，不要多余文本。"
    };

    const userMessage = {
      role: "user",
      content: `
症状：${symptom || "无"}
检查/报告：${report || "无"}
关注点：${target || "无"}

只返回 JSON（不要markdown、不要多余文本）：
{"summary":["...","...","..."],"questions":["...","...","..."],"notes":["...","..."]}

规则：
- summary：3条，事实性整理/复述
- questions：3条，必须是“问医生的问题句”
- notes：2条，中性提醒，不含诊断/治疗建议
`.trim()
    };

    const content = await callDashScopeFast([systemMessage, userMessage]);

    const data = parseStrictJson(content);

    // 如果模型输出不符合，给一个兜底，避免前端挂
    if (!data.summary.length && !data.questions.length && !data.notes.length) {
      return { code: 500, message: "模型输出为空/不符合格式" };
    }

    return { code: 0, data };
  } catch (err) {
    // 常见：2500ms timeout / 401 / 网络抖动
    console.error("prepareConsult error:", err?.message || err);

    // 把 axios 超时变成更可读的提示（前端能提示用户重试）
    if (String(err?.message || "").includes("timeout")) {
      return { code: 504, message: "生成超时，请重试（网络或模型响应较慢）" };
    }

    return { code: 500, message: err?.message || "server error" };
  }
};
