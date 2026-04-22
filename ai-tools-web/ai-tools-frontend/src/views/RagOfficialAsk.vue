<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { API, apiUrl, logApiFailure } from '../api.js'
import { trackApiFail, trackApiSuccess, trackSubmit } from '../analytics.js'
import { httpErrorMessage, NETWORK_UNREACHABLE, RESPONSE_PARSE_ERROR } from '../clientErrors.js'
import ErrorDialog from '../components/ErrorDialog.vue'

const kbId = ref('')
const kbList = ref([])
const question = ref('')
const topK = ref(3)
const askResult = ref(null)
const loadingKbs = ref(false)
const loadingAsk = ref(false)
const errorDialog = ref(false)
const errorText = ref('')

function showErrorDetail(text) {
  errorText.value = text
  errorDialog.value = true
}

async function loadOfficialKbs() {
  loadingKbs.value = true
  const url = apiUrl(API.ragKbs)
  try {
    const res = await fetch(url)
    if (!res.ok) {
      await logApiFailure(url, null, res, new Error(`HTTP ${res.status}`))
      return showErrorDetail(httpErrorMessage(res.status))
    }
    const payload = await res.json()
    if (payload?.code !== 0 || !Array.isArray(payload?.data)) {
      return showErrorDetail(payload?.message || '加载知识库失败')
    }
    kbList.value = payload.data.filter((kb) => kb.source_type === 'official' && kb.is_selectable)
    if (!kbId.value && kbList.value.length > 0) kbId.value = kbList.value[0].id
  } catch (e) {
    await logApiFailure(url, null, null, e)
    showErrorDetail(NETWORK_UNREACHABLE)
  } finally {
    loadingKbs.value = false
  }
}

async function askRag() {
  if (!kbId.value) return showErrorDetail('当前没有可用官方模板库，请联系管理员发布模板')
  const q = question.value.trim()
  if (!q) return showErrorDetail('请先输入问题')
  loadingAsk.value = true
  const requestStart = Date.now()
  const trackEventId = trackSubmit('rag_official_ask', '/rag/official')
  const url = apiUrl(API.ragAsk)
  const requestBody = { kb_id: kbId.value, query: q, top_k: Number(topK.value) || 3 }
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    })
    if (!res.ok) {
      await logApiFailure(url, requestBody, res, new Error(`HTTP ${res.status}`))
      trackApiFail('rag_official_ask', '/rag/official', trackEventId, `http_${res.status}`, Date.now() - requestStart)
      return showErrorDetail(httpErrorMessage(res.status))
    }
    let payload
    try {
      payload = await res.json()
    } catch (parseErr) {
      await logApiFailure(url, requestBody, res, parseErr)
      trackApiFail('rag_official_ask', '/rag/official', trackEventId, 'response_parse_error', Date.now() - requestStart)
      return showErrorDetail(RESPONSE_PARSE_ERROR)
    }
    if (payload?.code !== 0) {
      trackApiFail(
        'rag_official_ask',
        '/rag/official',
        trackEventId,
        payload?.code != null ? `business_${payload.code}` : 'business_error',
        Date.now() - requestStart,
      )
      return showErrorDetail(payload?.message || '问答失败')
    }
    trackApiSuccess('rag_official_ask', '/rag/official', trackEventId, Date.now() - requestStart)
    askResult.value = payload.data
  } catch (e) {
    await logApiFailure(url, requestBody, null, e)
    trackApiFail('rag_official_ask', '/rag/official', trackEventId, 'network_error', Date.now() - requestStart)
    showErrorDetail(NETWORK_UNREACHABLE)
  } finally {
    loadingAsk.value = false
  }
}

onMounted(() => {
  loadOfficialKbs()
})
</script>

<template>
  <div class="page">
    <header class="nav">
      <RouterLink class="back" to="/rag">← 返回模式页</RouterLink>
    </header>
    <section class="card">
      <h1 class="title">模式 B：官方模板直接提问</h1>
      <p class="sub">不需要创建知识库和上传文档，直接选择官方模板库提问。</p>
    </section>
    <section class="card">
      <h2 class="block-title">1）选择官方模板库</h2>
      <select v-model="kbId" class="input">
        <option value="" disabled>请选择官方模板库</option>
        <option v-for="kb in kbList" :key="kb.id" :value="kb.id">{{ kb.name }}</option>
      </select>
      <button class="btn btn-soft" :disabled="loadingKbs" @click="loadOfficialKbs">{{ loadingKbs ? '刷新中…' : '刷新模板库' }}</button>
    </section>
    <section class="card">
      <h2 class="block-title">2）提问</h2>
      <textarea v-model="question" class="textarea" rows="4" placeholder="输入问题" />
      <details class="advanced">
        <summary>高级设置（可选）</summary>
        <label class="meta">TopK（建议 3）</label>
        <input v-model.number="topK" class="input" type="number" min="1" max="8" />
      </details>
      <button class="btn btn-gradient" :disabled="loadingAsk" @click="askRag">{{ loadingAsk ? '生成中…' : '开始问答' }}</button>
    </section>
    <section class="card" v-if="askResult">
      <h2 class="block-title">回答</h2>
      <pre class="answer">{{ askResult.answer }}</pre>
    </section>
    <ErrorDialog v-model="errorDialog" :text="errorText" />
  </div>
</template>

<style scoped>
.page { max-width: 760px; margin: 0 auto; padding: 16px 12px 40px; min-height: 100vh; }
.nav { padding: 4px 4px 14px; }
.back { font-size: 14px; font-weight: 500; color: #6366f1; text-decoration: none; }
.card { background: rgba(255,255,255,.9); border-radius: 18px; padding: 18px 16px; margin-bottom: 14px; border: 1px solid rgba(148,163,184,.22); box-shadow: 0 4px 24px rgba(15,23,42,.06); }
.title { font-size: 21px; font-weight: 800; margin: 0 0 8px; }
.sub { margin: 0; color: #64748b; font-size: 14px; }
.block-title { font-size: 15px; font-weight: 700; margin: 0 0 12px; color: #0f172a; }
.input, .textarea { width: 100%; border-radius: 12px; border: 1px solid rgba(148,163,184,.3); background: #f8fafc; color: #0f172a; padding: 10px 12px; margin-bottom: 10px; }
.textarea { resize: vertical; line-height: 1.55; }
.btn { width: 100%; padding: 12px 14px; border-radius: 12px; font-size: 14px; font-weight: 600; }
.btn-soft { border: 1px solid rgba(99,102,241,.35); color: #4338ca; background: #fff; }
.meta { margin: 8px 0 0; font-size: 12px; color: #64748b; word-break: break-all; }
.advanced { margin: 8px 0 10px; }
.advanced summary { cursor: pointer; color: #475569; font-size: 13px; font-weight: 600; margin-bottom: 8px; }
.answer { white-space: pre-wrap; margin: 8px 0 0; padding: 12px; border-radius: 12px; background: #f8fafc; border: 1px solid rgba(148,163,184,.25); }
</style>
