<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { API, apiUrl, logApiFailure } from '../api.js'
import { trackApiFail, trackApiSuccess, trackSubmit } from '../analytics.js'
import {
  httpErrorMessage,
  NETWORK_UNREACHABLE,
  RESPONSE_PARSE_ERROR,
} from '../clientErrors.js'
import ErrorDialog from '../components/ErrorDialog.vue'

const inputText = ref('')
const loading = ref(false)
const result = ref(null)
const errorDialog = ref(false)
const errorText = ref('')
const examplePrompts = [
  '老板让我下周上线新功能，但需求还在变、测试时间又不够，我该怎么推进？',
  '用户持续投诉客服回复慢、满意度下降，团队应该优先改哪些环节？',
  '我总是制定学习计划却执行不下去，怎么做一个能坚持的学习方案？',
]

function showErrorDetail(text) {
  errorText.value = text
  errorDialog.value = true
}

function useExamplePrompt(prompt) {
  inputText.value = prompt
}

async function onCompare() {
  const text = (inputText.value || '').trim()
  if (!text) {
    showErrorDetail('请先输入要对比的内容。')
    return
  }

  loading.value = true
  const requestStart = Date.now()
  const trackEventId = trackSubmit('model_compare', '/model-compare')
  const url = apiUrl(API.modelCompare)
  const requestBody = { input: text }
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    })

    if (!res.ok) {
      await logApiFailure(url, requestBody, res, new Error(`HTTP ${res.status}`))
      trackApiFail('model_compare', '/model-compare', trackEventId, `http_${res.status}`, Date.now() - requestStart)
      showErrorDetail(httpErrorMessage(res.status))
      return
    }

    let r
    try {
      r = await res.json()
    } catch (parseErr) {
      await logApiFailure(url, requestBody, res, parseErr)
      trackApiFail('model_compare', '/model-compare', trackEventId, 'response_parse_error', Date.now() - requestStart)
      showErrorDetail(RESPONSE_PARSE_ERROR)
      return
    }

    if (r?.code !== 0) {
      trackApiFail(
        'model_compare',
        '/model-compare',
        trackEventId,
        r?.code != null ? `business_${r.code}` : 'business_error',
        Date.now() - requestStart,
      )
      showErrorDetail(
        r?.message ||
          '【原因】模型对比未成功。\n【怎么办】请稍后重试，或缩短输入内容后再试。',
      )
      return
    }

    trackApiSuccess('model_compare', '/model-compare', trackEventId, Date.now() - requestStart)
    result.value = r.data ?? null
  } catch (e) {
    await logApiFailure(url, requestBody, null, e)
    trackApiFail('model_compare', '/model-compare', trackEventId, 'network_error', Date.now() - requestStart)
    showErrorDetail(NETWORK_UNREACHABLE)
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

    <header class="header">
      <h1 class="title">模型优化实验 / 微调效果对比</h1>
      <p class="sub">
        该功能用于对比原始模型与优化模型在特定场景下的输出差异，优化模型当前为占位实现，后续可替换为真实微调模型。
      </p>
    </header>

    <section class="card">
      <div class="label">输入内容</div>
      <p class="input-tip">
        建议输入具体场景问题（如项目推进、客服优化、学习规划），更容易看出优化模型在结构化与可控性上的差异。
      </p>
      <div class="example-wrap">
        <button
          v-for="(prompt, idx) in examplePrompts"
          :key="'example-' + idx"
          type="button"
          class="example-btn"
          @click="useExamplePrompt(prompt)"
        >
          示例{{ idx + 1 }}：{{ prompt }}
        </button>
      </div>
      <textarea
        v-model="inputText"
        class="textarea"
        placeholder="请输入你希望进行对比的问题或任务..."
        rows="8"
        spellcheck="false"
      />
      <button
        type="button"
        class="btn btn-gradient"
        :disabled="loading"
        @click="onCompare"
      >
        {{ loading ? '对比中…' : '开始对比' }}
      </button>
      <p class="result-tip">
        对比提示：原始模型通常是自由回答；优化模型应尽量按【核心问题】【分析】【建议】三段输出。
      </p>
    </section>

    <section class="compare-grid">
      <div class="card">
        <h2 class="block-title">原始模型输出</h2>
        <p v-if="!result?.original_output" class="empty">点击「开始对比」后显示</p>
        <pre v-else class="output">{{ result.original_output }}</pre>
      </div>

      <div class="card">
        <h2 class="block-title">优化模型输出</h2>
        <p v-if="!result?.optimized_output" class="empty">点击「开始对比」后显示</p>
        <pre v-else class="output">{{ result.optimized_output }}</pre>
      </div>
    </section>

    <ErrorDialog v-model="errorDialog" :text="errorText" />
  </div>
</template>

<style scoped>
.page {
  padding: 16px 12px 40px;
  max-width: 1100px;
  margin: 0 auto;
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

.header {
  margin-bottom: 18px;
  padding: 4px 4px 0;
}

.title {
  font-size: 22px;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin: 0;
  line-height: 1.3;
  color: #0f172a;
}

.sub {
  margin: 10px 0 0;
  font-size: 14px;
  color: var(--text-muted, #64748b);
  line-height: 1.65;
}

.card {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-radius: var(--radius, 18px);
  padding: 18px 16px;
  margin-bottom: 14px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  box-shadow: var(--shadow-card, 0 4px 24px rgba(15, 23, 42, 0.06));
}

.label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 10px;
}

.input-tip {
  margin: 0 0 10px;
  font-size: 13px;
  line-height: 1.6;
  color: #64748b;
}

.example-wrap {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.example-btn {
  border: 1px solid rgba(99, 102, 241, 0.28);
  background: rgba(238, 242, 255, 0.65);
  color: #4338ca;
  font-size: 12px;
  line-height: 1.4;
  border-radius: 999px;
  padding: 6px 10px;
  text-align: left;
}

.example-btn:hover {
  background: rgba(224, 231, 255, 0.9);
}

.textarea {
  width: 100%;
  min-height: 140px;
  padding: 14px;
  border-radius: 14px;
  background: rgba(241, 245, 249, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.22);
  font-size: 15px;
  color: #0f172a;
  resize: vertical;
  line-height: 1.55;
}

.textarea:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.45);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.btn {
  width: 100%;
  margin-top: 14px;
  padding: 14px 16px;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 600;
  text-align: center;
}

.result-tip {
  margin: 10px 2px 0;
  font-size: 12px;
  line-height: 1.6;
  color: #64748b;
}

.compare-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 14px;
}

@media (min-width: 920px) {
  .compare-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.block-title {
  font-size: 15px;
  font-weight: 700;
  margin: 0 0 12px;
  color: #0f172a;
}

.empty {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}

.output {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  line-height: 1.65;
  color: #1e293b;
  font-size: 14px;
  font-family: inherit;
}
</style>
