<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { API, apiUrl, logApiFailure } from '../api.js'
import { trackApiFail, trackApiSuccess, trackPageView, trackSubmit } from '../analytics.js'
import { NETWORK_UNREACHABLE, RESPONSE_PARSE_ERROR, httpErrorMessage } from '../clientErrors.js'
import ErrorDialog from '../components/ErrorDialog.vue'

const PAGE_PATH = '/tools/memory-compare'
const FEATURE = 'memory_compare'

const form = ref({
  chatContent: '',
  question: '',
})
const loading = ref(false)
const result = ref(null)
const errorDialog = ref(false)
const errorText = ref('')

onMounted(() => {
  trackPageView(PAGE_PATH)
})

function showError(text) {
  errorText.value = text
  errorDialog.value = true
}

async function onSubmit() {
  const chatContent = (form.value.chatContent || '').trim()
  const question = (form.value.question || '').trim()
  if (!chatContent) {
    showError('请先填写聊天记录。')
    return
  }
  if (!question) {
    showError('请先填写用户问题。')
    return
  }

  loading.value = true
  result.value = null
  const requestStart = Date.now()
  const trackEventId = trackSubmit(FEATURE, PAGE_PATH)
  const url = apiUrl(API.memoryCompare)
  const requestBody = {
    chat_content: chatContent,
    question,
  }

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    })

    if (!res.ok) {
      await logApiFailure(url, requestBody, res, new Error(`HTTP ${res.status}`))
      trackApiFail(FEATURE, PAGE_PATH, trackEventId, `http_${res.status}`, Date.now() - requestStart)
      showError(httpErrorMessage(res.status))
      return
    }

    let payload
    try {
      payload = await res.json()
    } catch (parseErr) {
      await logApiFailure(url, requestBody, res, parseErr)
      trackApiFail(FEATURE, PAGE_PATH, trackEventId, 'response_parse_error', Date.now() - requestStart)
      showError(RESPONSE_PARSE_ERROR)
      return
    }

    if (!payload || payload.code !== 0 || !payload.data) {
      trackApiFail(
        FEATURE,
        PAGE_PATH,
        trackEventId,
        payload?.code != null ? `business_${payload.code}` : 'business_error',
        Date.now() - requestStart,
      )
      showError(payload?.message || '本次分析失败，请稍后再试。')
      return
    }

    trackApiSuccess(FEATURE, PAGE_PATH, trackEventId, Date.now() - requestStart)
    result.value = payload.data
  } catch (err) {
    await logApiFailure(url, requestBody, null, err)
    trackApiFail(FEATURE, PAGE_PATH, trackEventId, 'network_error', Date.now() - requestStart)
    showError(NETWORK_UNREACHABLE)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page">
    <nav class="top-nav">
      <RouterLink class="nav-link" to="/">← 首页</RouterLink>
    </nav>

    <section class="card header">
      <h1 class="title">AI 记忆对比助手</h1>
      <p class="sub">用于演示“AI有无记忆”的差别：同一个问题，对比通用回答和个性化回答。</p>
      <div class="scene-box">
        <p class="scene-title">这个工具解决什么问题？</p>
        <p>很多用户看不出 AI 是否真的“记住了我”。这个页面会把两种回答并排展示，直观看差异。</p>
        <p class="scene-title">你应该输入什么？</p>
        <p>聊天记录里填用户背景（身份、目标、困扰、限制条件等）；问题里填当前最想问的一句话。</p>
      </div>
      <div class="notice">
        <p class="notice-title">对比规则（先看这个）</p>
        <p>左侧普通AI：只读取“用户问题”，不读取聊天记录。</p>
        <p>右侧记忆增强AI：先从本次输入的聊天记录抽取结构化记忆，再回答问题。</p>
        <p>本工具不会提前从库里读取你的历史数据；记忆仅来自你这次输入内容。</p>
      </div>
    </section>

    <section class="card">
      <label class="field">
        <span class="label">聊天记录</span>
        <textarea
          v-model="form.chatContent"
          class="input textarea"
          placeholder="例如：我是UI设计师，最近在考虑未来发展方向，担心岗位成长空间有限，也在犹豫要不要转向产品方向。"
        />
      </label>
      <label class="field">
        <span class="label">用户问题</span>
        <input v-model="form.question" class="input" placeholder="例如：我下一步该优先提升专业深度，还是尝试转岗？" />
      </label>
      <button type="button" class="btn btn-gradient" :disabled="loading" @click="onSubmit">
        {{ loading ? '分析中…' : '开始分析' }}
      </button>
    </section>

    <section class="compare-grid">
      <article class="card answer-card normal">
        <div class="answer-head">
          <span class="answer-icon">❌ 普通AI</span>
          <span class="answer-rule">仅使用问题</span>
        </div>
        <h2 class="answer-title">不带记忆的回答</h2>
        <p v-if="!result" class="empty">点击「开始分析」后显示</p>
        <p v-else class="answer-text">{{ result.normal_answer || '暂无结果' }}</p>
      </article>

      <article class="card answer-card memory">
        <div class="answer-head">
          <span class="answer-icon">✅ 记忆增强AI</span>
          <div class="head-tags">
            <span class="answer-rule memory-rule">读取聊天记录</span>
            <span class="memory-tag">更懂你</span>
          </div>
        </div>
        <h2 class="answer-title">结合你的历史情况的回答</h2>
        <p v-if="!result" class="empty">点击「开始分析」后显示</p>
        <p v-else class="answer-text">{{ result.memory_answer || '暂无结果' }}</p>
      </article>
    </section>

    <section v-if="result?.structured_memory" class="card">
      <h3 class="memory-title">右侧 AI 使用的结构化记忆（仅本次输入）</h3>
      <div class="memory-grid">
        <p><strong>职业：</strong>{{ result.structured_memory.职业 || '未提取到' }}</p>
        <p><strong>目标：</strong>{{ result.structured_memory.目标 || '未提取到' }}</p>
        <p><strong>情绪：</strong>{{ result.structured_memory.情绪 || '未提取到' }}</p>
        <p><strong>风险倾向：</strong>{{ result.structured_memory.风险倾向 || '未提取到' }}</p>
        <p class="events">
          <strong>关键事件：</strong>
          {{
            Array.isArray(result.structured_memory.关键事件) && result.structured_memory.关键事件.length
              ? result.structured_memory.关键事件.join('；')
              : '未提取到'
          }}
        </p>
      </div>
    </section>

    <ErrorDialog v-model="errorDialog" :text="errorText" />
  </div>
</template>

<style scoped>
.page {
  max-width: 980px;
  margin: 0 auto;
  padding: 16px 12px 40px;
  min-height: 100vh;
}

.top-nav {
  padding: 0 4px 12px;
}

.nav-link {
  font-size: 14px;
  font-weight: 500;
  color: #6366f1;
  text-decoration: none;
}

.card {
  background: rgba(255, 255, 255, 0.92);
  border-radius: var(--radius, 18px);
  padding: 18px 16px;
  margin-bottom: 14px;
  border: var(--border-soft, 1px solid rgba(148, 163, 184, 0.22));
  box-shadow: var(--shadow-card, 0 4px 24px rgba(15, 23, 42, 0.06));
}

.header .title {
  margin: 0 0 8px;
  font-size: 22px;
  font-weight: 800;
  color: #0f172a;
}

.sub {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.scene-box {
  margin-top: 12px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.3);
  background: linear-gradient(135deg, rgba(248, 250, 252, 0.95), rgba(241, 245, 249, 0.9));
  padding: 10px 12px;
}

.scene-title {
  margin: 0 0 4px;
  font-size: 13px;
  font-weight: 700;
  color: #0f172a;
}

.scene-box p {
  margin: 0 0 8px;
  color: #334155;
  font-size: 13px;
  line-height: 1.6;
}

.scene-box p:last-child {
  margin-bottom: 0;
}

.notice {
  margin-top: 12px;
  border-radius: 12px;
  border: 1px solid rgba(99, 102, 241, 0.2);
  background: linear-gradient(135deg, rgba(238, 242, 255, 0.9), rgba(240, 249, 255, 0.85));
  padding: 10px 12px;
}

.notice-title {
  margin: 0 0 6px;
  font-size: 13px;
  font-weight: 700;
  color: #3730a3;
}

.notice p {
  margin: 0 0 4px;
  color: #334155;
  font-size: 13px;
  line-height: 1.6;
}

.notice p:last-child {
  margin-bottom: 0;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 12px;
}

.label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
}

.input {
  width: 100%;
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(241, 245, 249, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.22);
  font-size: 14px;
  color: #0f172a;
}

.textarea {
  min-height: 130px;
  resize: vertical;
}

.input:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.45);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.btn {
  width: 100%;
  margin-top: 2px;
  padding: 14px 16px;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 600;
}

.compare-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}

.answer-card {
  margin-bottom: 0;
}

.normal {
  border: 1px solid rgba(248, 113, 113, 0.35);
  background: linear-gradient(135deg, rgba(254, 226, 226, 0.56), rgba(255, 255, 255, 0.96));
}

.memory {
  border: 1px solid rgba(16, 185, 129, 0.35);
  background: linear-gradient(135deg, rgba(209, 250, 229, 0.58), rgba(255, 255, 255, 0.96));
}

.answer-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-bottom: 8px;
}

.answer-icon {
  font-size: 14px;
  font-weight: 700;
}

.head-tags {
  display: flex;
  align-items: center;
  gap: 8px;
}

.answer-rule {
  font-size: 11px;
  font-weight: 700;
  color: #991b1b;
  background: rgba(248, 113, 113, 0.14);
  border: 1px solid rgba(248, 113, 113, 0.35);
  border-radius: 999px;
  padding: 4px 8px;
}

.memory-rule {
  color: #065f46;
  background: rgba(16, 185, 129, 0.16);
  border-color: rgba(16, 185, 129, 0.35);
}

.memory-tag {
  font-size: 12px;
  font-weight: 700;
  color: #047857;
  background: rgba(16, 185, 129, 0.18);
  border: 1px solid rgba(16, 185, 129, 0.35);
  border-radius: 999px;
  padding: 4px 10px;
}

.answer-title {
  margin: 0 0 10px;
  font-size: 16px;
  font-weight: 700;
  color: #0f172a;
}

.answer-text {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.72;
  color: #1f2937;
  font-size: 14px;
}

.empty {
  margin: 0;
  color: #94a3b8;
  font-size: 14px;
}

.memory-title {
  margin: 0 0 8px;
  font-size: 15px;
  color: #0f172a;
}

.memory-grid p {
  margin: 0 0 6px;
  color: #334155;
  font-size: 14px;
}

.memory-grid p:last-child {
  margin-bottom: 0;
}

.events {
  line-height: 1.65;
}

@media (min-width: 880px) {
  .compare-grid {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
