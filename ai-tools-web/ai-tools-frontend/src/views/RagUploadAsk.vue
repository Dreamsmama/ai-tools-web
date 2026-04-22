<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { API, apiUrl, logApiFailure } from '../api.js'
import { trackApiFail, trackApiSuccess, trackSubmit } from '../analytics.js'
import { httpErrorMessage, NETWORK_UNREACHABLE, RESPONSE_PARSE_ERROR } from '../clientErrors.js'
import ErrorDialog from '../components/ErrorDialog.vue'

const kbName = ref('')
const kbDescription = ref('')
const kbId = ref('')
const question = ref('')
const topK = ref(3)
const selectedFile = ref(null)
const documentInfo = ref(null)
const askResult = ref(null)
const loadingCreateKb = ref(false)
const loadingUpload = ref(false)
const loadingIngest = ref(false)
const loadingAsk = ref(false)
const toast = ref('')
const errorDialog = ref(false)
const errorText = ref('')
const recommendedExtensions = ['txt', 'md', 'json', 'csv', 'log']
const statusLabelMap = {
  uploaded: '已上传',
  parsing: '解析中',
  parsed: '已解析',
  embedding: '向量化中',
  indexed: '已入库',
  failed: '失败',
}

function statusLabel(status) {
  return statusLabelMap[status] || status || '未知'
}

function showToast(message) {
  toast.value = message
  window.setTimeout(() => {
    toast.value = ''
  }, 2200)
}

function showErrorDetail(text) {
  errorText.value = text
  errorDialog.value = true
}

function onFileChange(event) {
  const file = event?.target?.files?.[0] || null
  selectedFile.value = file
  if (!file) return
  const ext = (file.name.split('.').pop() || '').toLowerCase()
  if (!recommendedExtensions.includes(ext)) {
    showToast('该格式可尝试上传，但当前推荐 txt/md/json/csv/log')
  }
  if (file.size < 20) {
    showToast('文件内容过少，检索效果可能不稳定')
  }
}

async function createKb() {
  const name = kbName.value.trim()
  if (!name) return showToast('请先填写知识库名称')
  loadingCreateKb.value = true
  const requestStart = Date.now()
  const trackEventId = trackSubmit('rag_upload_ask', '/rag/upload')
  const url = apiUrl(API.ragKbs)
  const requestBody = { name, description: kbDescription.value.trim() }
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    })
    if (!res.ok) {
      await logApiFailure(url, requestBody, res, new Error(`HTTP ${res.status}`))
      trackApiFail('rag_upload_ask', '/rag/upload', trackEventId, `http_${res.status}`, Date.now() - requestStart)
      return showErrorDetail(httpErrorMessage(res.status))
    }
    const payload = await res.json()
    if (payload?.code !== 0 || !payload?.data?.id) {
      trackApiFail(
        'rag_upload_ask',
        '/rag/upload',
        trackEventId,
        payload?.code != null ? `business_${payload.code}` : 'business_error',
        Date.now() - requestStart,
      )
      return showErrorDetail(payload?.message || '创建知识库失败')
    }
    trackApiSuccess('rag_upload_ask', '/rag/upload', trackEventId, Date.now() - requestStart)
    kbId.value = payload.data.id
    kbName.value = ''
    kbDescription.value = ''
    showToast('知识库创建成功')
  } catch (e) {
    await logApiFailure(url, requestBody, null, e)
    trackApiFail('rag_upload_ask', '/rag/upload', trackEventId, 'network_error', Date.now() - requestStart)
    showErrorDetail(NETWORK_UNREACHABLE)
  } finally {
    loadingCreateKb.value = false
  }
}

async function uploadDocument() {
  if (!kbId.value) return showToast('请先创建知识库')
  if (!selectedFile.value) return showToast('请先选择文件')
  loadingUpload.value = true
  const requestStart = Date.now()
  const trackEventId = trackSubmit('rag_upload_ask', '/rag/upload')
  const url = apiUrl(API.ragUpload)
  const formData = new FormData()
  formData.append('kb_id', kbId.value)
  formData.append('file', selectedFile.value)
  try {
    const res = await fetch(url, { method: 'POST', body: formData })
    if (!res.ok) {
      await logApiFailure(url, { kbId: kbId.value }, res, new Error(`HTTP ${res.status}`))
      trackApiFail('rag_upload_ask', '/rag/upload', trackEventId, `http_${res.status}`, Date.now() - requestStart)
      return showErrorDetail(httpErrorMessage(res.status))
    }
    const payload = await res.json()
    if (payload?.code !== 0 || !payload?.data?.id) {
      trackApiFail(
        'rag_upload_ask',
        '/rag/upload',
        trackEventId,
        payload?.code != null ? `business_${payload.code}` : 'business_error',
        Date.now() - requestStart,
      )
      return showErrorDetail(payload?.message || '上传文档失败')
    }
    trackApiSuccess('rag_upload_ask', '/rag/upload', trackEventId, Date.now() - requestStart)
    documentInfo.value = payload.data
    showToast('文档上传成功')
  } catch (e) {
    await logApiFailure(url, { kbId: kbId.value }, null, e)
    trackApiFail('rag_upload_ask', '/rag/upload', trackEventId, 'network_error', Date.now() - requestStart)
    showErrorDetail(NETWORK_UNREACHABLE)
  } finally {
    loadingUpload.value = false
  }
}

async function ingestDocument() {
  if (!documentInfo.value?.id) return showToast('请先上传文档')
  loadingIngest.value = true
  const requestStart = Date.now()
  const trackEventId = trackSubmit('rag_upload_ask', '/rag/upload')
  const url = apiUrl(API.ragIngest(documentInfo.value.id))
  try {
    const res = await fetch(url, { method: 'POST' })
    if (!res.ok) {
      await logApiFailure(url, { documentId: documentInfo.value.id }, res, new Error(`HTTP ${res.status}`))
      trackApiFail('rag_upload_ask', '/rag/upload', trackEventId, `http_${res.status}`, Date.now() - requestStart)
      return showErrorDetail(httpErrorMessage(res.status))
    }
    const payload = await res.json()
    if (payload?.code !== 0) {
      trackApiFail(
        'rag_upload_ask',
        '/rag/upload',
        trackEventId,
        payload?.code != null ? `business_${payload.code}` : 'business_error',
        Date.now() - requestStart,
      )
      return showErrorDetail(payload?.message || '文档入库失败')
    }
    trackApiSuccess('rag_upload_ask', '/rag/upload', trackEventId, Date.now() - requestStart)
    documentInfo.value = payload.data
    showToast(`入库完成，状态：${statusLabel(payload.data?.status)}`)
  } catch (e) {
    await logApiFailure(url, { documentId: documentInfo.value.id }, null, e)
    trackApiFail('rag_upload_ask', '/rag/upload', trackEventId, 'network_error', Date.now() - requestStart)
    showErrorDetail(NETWORK_UNREACHABLE)
  } finally {
    loadingIngest.value = false
  }
}

async function askRag() {
  if (!kbId.value) return showToast('请先创建知识库')
  const q = question.value.trim()
  if (!q) return showToast('请先输入问题')
  loadingAsk.value = true
  const requestStart = Date.now()
  const trackEventId = trackSubmit('rag_upload_ask', '/rag/upload')
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
      trackApiFail('rag_upload_ask', '/rag/upload', trackEventId, `http_${res.status}`, Date.now() - requestStart)
      return showErrorDetail(httpErrorMessage(res.status))
    }
    const payload = await res.json()
    if (payload?.code !== 0) {
      trackApiFail(
        'rag_upload_ask',
        '/rag/upload',
        trackEventId,
        payload?.code != null ? `business_${payload.code}` : 'business_error',
        Date.now() - requestStart,
      )
      return showErrorDetail(payload?.message || '问答失败')
    }
    trackApiSuccess('rag_upload_ask', '/rag/upload', trackEventId, Date.now() - requestStart)
    askResult.value = payload.data
  } catch (e) {
    await logApiFailure(url, requestBody, null, e)
    trackApiFail('rag_upload_ask', '/rag/upload', trackEventId, 'network_error', Date.now() - requestStart)
    showErrorDetail(NETWORK_UNREACHABLE)
  } finally {
    loadingAsk.value = false
  }
}
</script>

<template>
  <div class="page">
    <header class="nav">
      <RouterLink class="back" to="/rag">← 返回模式页</RouterLink>
    </header>
    <section class="card">
      <h1 class="title">模式 A：上传文档后提问</h1>
      <p class="sub">创建知识库 -> 上传文档 -> 执行入库 -> 提问。</p>
    </section>
    <section class="card">
      <h2 class="block-title">1）创建知识库</h2>
      <input v-model="kbName" class="input" placeholder="知识库名称" />
      <textarea v-model="kbDescription" class="textarea" rows="3" placeholder="知识库描述（可选）" />
      <button class="btn btn-gradient" :disabled="loadingCreateKb" @click="createKb">
        {{ loadingCreateKb ? '创建中…' : '创建知识库' }}
      </button>
      <p v-if="kbId" class="meta">当前 kb_id：{{ kbId }}</p>
    </section>
    <section class="card">
      <h2 class="block-title">2）上传文档并入库</h2>
      <input class="input-file" type="file" @change="onFileChange" />
      <div class="tips">
        <p class="tip-title">格式提醒</p>
        <p class="tip-item">推荐格式：txt / md / json / csv / log</p>
        <p class="tip-item">暂不推荐：pdf / docx（当前解析能力有限）</p>
      </div>
      <div class="tips">
        <p class="tip-title">内容提示</p>
        <p class="tip-item">一份文档尽量聚焦一个主题，关键事实用完整短句表达。</p>
        <p class="tip-item">示例：退款审核通过后，系统会在 3 个工作日内原路退回。</p>
      </div>
      <div class="row-actions">
        <button class="btn btn-soft" :disabled="loadingUpload" @click="uploadDocument">{{ loadingUpload ? '上传中…' : '上传文档' }}</button>
        <button class="btn btn-soft" :disabled="loadingIngest" @click="ingestDocument">{{ loadingIngest ? '入库中…' : '执行入库' }}</button>
      </div>
      <p v-if="documentInfo?.id" class="meta">文档：{{ documentInfo.filename }} ｜ 状态：{{ statusLabel(documentInfo.status) }}</p>
    </section>
    <section class="card">
      <h2 class="block-title">3）提问</h2>
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
    <div v-if="toast" class="toast">{{ toast }}</div>
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
.input-file { margin-bottom: 10px; }
.tips {
  margin: 0 0 10px;
  padding: 10px 12px;
  border-radius: 12px;
  background: #f8fafc;
  border: 1px solid rgba(148,163,184,.25);
}
.tip-title {
  margin: 0 0 4px;
  font-size: 12px;
  font-weight: 700;
  color: #475569;
}
.tip-item {
  margin: 0;
  font-size: 12px;
  color: #64748b;
  line-height: 1.6;
}
.row-actions { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.btn { width: 100%; padding: 12px 14px; border-radius: 12px; font-size: 14px; font-weight: 600; }
.btn-soft { border: 1px solid rgba(99,102,241,.35); color: #4338ca; background: #fff; }
.meta { margin: 8px 0 0; font-size: 12px; color: #64748b; word-break: break-all; }
.advanced { margin: 8px 0 10px; }
.advanced summary { cursor: pointer; color: #475569; font-size: 13px; font-weight: 600; margin-bottom: 8px; }
.answer { white-space: pre-wrap; margin: 8px 0 0; padding: 12px; border-radius: 12px; background: #f8fafc; border: 1px solid rgba(148,163,184,.25); }
.toast { position: fixed; left: 50%; bottom: 48px; transform: translateX(-50%); padding: 12px 20px; border-radius: 999px; background: rgba(15,23,42,.88); color: #fff; font-size: 14px; z-index: 2000; }
</style>
