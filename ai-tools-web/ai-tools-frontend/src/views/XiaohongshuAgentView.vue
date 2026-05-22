<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { API, apiUrl, logApiFailure } from '../api.js'
import { trackApiFail, trackApiSuccess, trackPageView, trackSubmit } from '../analytics.js'
import {
  httpErrorMessage,
  NETWORK_UNREACHABLE,
  RESPONSE_PARSE_ERROR,
} from '../clientErrors.js'
import ErrorDialog from '../components/ErrorDialog.vue'

const STYLE_OPTIONS = ['种草', '干货', '情绪', '测评', '清单']
const PAGE_PATH = '/xiaohongshu-agent'
const FEATURE = 'xiaohongshu_agent'

const form = ref({
  topic: '',
  product: '',
  audience: '',
  style: '种草',
  count: 3,
  generateImages: false,
})

const loading = ref(false)
const progressLabel = ref('')
const progressIndex = ref(0)
const progressTotal = ref(5)
const result = ref(null)
const toast = ref('')
const errorDialog = ref(false)
const errorText = ref('')

onMounted(() => {
  trackPageView(PAGE_PATH)
})

function showErrorDetail(text) {
  errorText.value = text
  errorDialog.value = true
}

function showToast(message) {
  toast.value = message
  window.setTimeout(() => {
    toast.value = ''
  }, 2200)
}

async function copyText(text, sectionName) {
  const value = (text || '').trim()
  if (!value) return
  try {
    await navigator.clipboard.writeText(value)
    trackSubmit(`${FEATURE}_copy_${sectionName}`, PAGE_PATH)
    showToast('已复制')
  } catch {
    showToast('复制失败，请手动选择复制')
  }
}

function copyLines(lines, sectionName) {
  if (!Array.isArray(lines) || lines.length === 0) return
  copyText(lines.join('\n'), sectionName)
}

function resetProgress() {
  progressLabel.value = ''
  progressIndex.value = 0
  progressTotal.value = form.value.generateImages ? 6 : 5
}

function onProgressEvent(data) {
  if (!data || data.type !== 'step') return
  progressIndex.value = Number(data.index) || 0
  progressTotal.value = Number(data.total) || progressTotal.value
  const label = data.label || data.step || '处理中'
  if (data.phase === 'start') {
    progressLabel.value = `${data.index}/${data.total} ${label}…`
  } else if (data.phase === 'done') {
    progressLabel.value = `${data.index}/${data.total} ${label} 完成`
  } else if (data.phase === 'failed') {
    progressLabel.value = `${data.index}/${data.total} ${label} 失败`
  }
}

/**
 * POST + SSE：解析 progress / result 事件（R8）。
 */
async function fetchXiaohongshuStream(url, requestBody, onProgress) {
  const res = await fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      Accept: 'text/event-stream',
    },
    body: JSON.stringify(requestBody),
  })
  if (!res.ok) {
    const err = new Error(`HTTP ${res.status}`)
    err.status = res.status
    throw err
  }
  if (!res.body) {
    throw new Error('浏览器不支持流式响应')
  }

  const reader = res.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let finalPayload = null

  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    const blocks = buffer.split('\n\n')
    buffer = blocks.pop() || ''
    for (const block of blocks) {
      const trimmed = block.trim()
      if (!trimmed) continue
      const eventLine = trimmed.match(/^event:\s*(.+)$/m)
      const dataLine = trimmed.match(/^data:\s*(.+)$/ms)
      const eventName = eventLine ? eventLine[1].trim() : 'message'
      const rawData = dataLine ? dataLine[1].trim() : ''
      if (!rawData) continue
      let parsed
      try {
        parsed = JSON.parse(rawData)
      } catch {
        continue
      }
      if (eventName === 'progress') {
        onProgress(parsed)
      } else if (eventName === 'result') {
        finalPayload = parsed
      }
    }
  }
  return finalPayload
}

async function fetchXiaohongshuJson(url, requestBody) {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(requestBody),
  })
  if (!res.ok) {
    const err = new Error(`HTTP ${res.status}`)
    err.status = res.status
    throw err
  }
  return res.json()
}

async function onGenerate() {
  const topic = (form.value.topic || '').trim()
  if (!topic) {
    showToast('请先填写内容主题')
    return
  }

  loading.value = true
  resetProgress()
  progressLabel.value = '准备中…'
  const requestStart = Date.now()
  const trackEventId = trackSubmit(FEATURE, PAGE_PATH)
  const streamUrl = apiUrl(API.xiaohongshuAgentGenerateStream)
  const jsonUrl = apiUrl(API.xiaohongshuAgentGenerate)
  const requestBody = {
    topic,
    product: (form.value.product || '').trim(),
    audience: (form.value.audience || '').trim(),
    style: (form.value.style || '种草').trim(),
    count: Number(form.value.count) || 3,
    generate_images: Boolean(form.value.generateImages),
  }
  try {
    let payload = null
    try {
      payload = await fetchXiaohongshuStream(streamUrl, requestBody, onProgressEvent)
    } catch (streamErr) {
      await logApiFailure(streamUrl, requestBody, null, streamErr)
      progressLabel.value = '流式不可用，改用普通请求…'
      payload = await fetchXiaohongshuJson(jsonUrl, requestBody)
    }

    if (!payload) {
      trackApiFail(FEATURE, PAGE_PATH, trackEventId, 'response_parse_error', Date.now() - requestStart)
      showErrorDetail(RESPONSE_PARSE_ERROR)
      return
    }

    if (payload.code !== 0) {
      trackApiFail(
        FEATURE,
        PAGE_PATH,
        trackEventId,
        payload?.code != null ? `business_${payload.code}` : 'business_error',
        Date.now() - requestStart,
      )
      showErrorDetail(
        payload?.message ||
          '【原因】本次未成功。\n【怎么办】无需改内容，直接再点一次提交试试，通常 1～2 次就会好。',
      )
      return
    }

    trackApiSuccess(FEATURE, PAGE_PATH, trackEventId, Date.now() - requestStart)
    result.value = payload.data ?? null
    progressLabel.value = '完成'
  } catch (err) {
    const status = err?.status
    if (status) {
      await logApiFailure(streamUrl, requestBody, { status }, err)
      trackApiFail(FEATURE, PAGE_PATH, trackEventId, `http_${status}`, Date.now() - requestStart)
      showErrorDetail(httpErrorMessage(status))
    } else {
      await logApiFailure(streamUrl, requestBody, null, err)
      trackApiFail(FEATURE, PAGE_PATH, trackEventId, 'network_error', Date.now() - requestStart)
      showErrorDetail(NETWORK_UNREACHABLE)
    }
  } finally {
    loading.value = false
    window.setTimeout(() => {
      if (!loading.value) progressLabel.value = ''
    }, 1500)
  }
}
</script>

<template>
  <div class="page">
    <nav class="top-nav">
      <RouterLink class="nav-link" to="/">← 首页</RouterLink>
    </nav>

    <header class="header card">
      <div class="title-wrap">
        <span class="title-accent" aria-hidden="true" />
        <div>
          <h1 class="title">小红书内容生产 Agent</h1>
          <p class="sub">输入主题、产品、人群与风格，一键生成标题、正文和图片提示词。</p>
        </div>
      </div>
    </header>

    <section class="card">
      <div class="grid">
        <label class="field">
          <span class="label">内容主题（必填）</span>
          <input v-model="form.topic" class="input" placeholder="例如：夏季通勤防晒穿搭" />
        </label>

        <label class="field">
          <span class="label">产品/服务（可选）</span>
          <input v-model="form.product" class="input" placeholder="例如：某防晒衣/某课程/某护肤品" />
        </label>

        <label class="field">
          <span class="label">目标人群（可选）</span>
          <input v-model="form.audience" class="input" placeholder="例如：25-35 岁通勤女性" />
        </label>

        <label class="field">
          <span class="label">内容风格</span>
          <select v-model="form.style" class="input">
            <option v-for="item in STYLE_OPTIONS" :key="item" :value="item">{{ item }}</option>
          </select>
        </label>

        <label class="field">
          <span class="label">输出数量</span>
          <input v-model.number="form.count" type="number" min="1" max="10" class="input" />
        </label>

        <label class="field field-check">
          <input v-model="form.generateImages" type="checkbox" class="checkbox" />
          <span class="label-inline">同时生成配图（即梦，较慢，需后端配置 JIMENG_API_KEY）</span>
        </label>
      </div>

      <button type="button" class="btn btn-gradient" :disabled="loading" @click="onGenerate">
        {{ loading ? (progressLabel || '生成中…') : '生成内容' }}
      </button>
      <div v-if="loading && progressTotal > 0" class="progress-wrap" role="status">
        <div class="progress-bar">
          <div
            class="progress-fill"
            :style="{ width: `${Math.min(100, (progressIndex / progressTotal) * 100)}%` }"
          />
        </div>
        <p class="progress-hint">{{ progressLabel }}</p>
      </div>
    </section>

    <section class="card">
      <div class="block-head">
        <h2 class="block-title">标题候选列表</h2>
        <button type="button" class="copy-btn" @click="copyLines(result?.titles, 'titles')">复制</button>
      </div>
      <p v-if="!result" class="empty">点击「生成内容」后显示</p>
      <p v-else-if="!result.titles?.length" class="empty">暂无结果</p>
      <p v-for="(item, idx) in result?.titles || []" :key="'title-' + idx" class="item">• {{ item }}</p>
    </section>

    <section class="card">
      <div class="block-head">
        <h2 class="block-title">正文文案</h2>
        <button type="button" class="copy-btn" @click="copyText(result?.content, 'content')">复制</button>
      </div>
      <p v-if="!result" class="empty">点击「生成内容」后显示</p>
      <p v-else-if="!result.content" class="empty">暂无结果</p>
      <div v-else class="text-block">{{ result.content }}</div>
    </section>

    <section class="card">
      <div class="block-head">
        <h2 class="block-title">图片生成提示词</h2>
        <button type="button" class="copy-btn" @click="copyLines(result?.image_prompts, 'image_prompts')">复制</button>
      </div>
      <p v-if="!result" class="empty">点击「生成内容」后显示</p>
      <p v-else-if="!result.image_prompts?.length" class="empty">暂无结果</p>
      <p v-for="(item, idx) in result?.image_prompts || []" :key="'img-' + idx" class="item">• {{ item }}</p>
    </section>

    <section class="card">
      <div class="block-head">
        <h2 class="block-title">配图预览</h2>
      </div>
      <p v-if="!result" class="empty">勾选「同时生成配图」且生成成功后会显示</p>
      <p v-else-if="!result.image_urls?.length" class="empty">本次未生成配图（未勾选或即梦未配置/失败）</p>
      <div v-else class="image-grid">
        <figure v-for="(url, idx) in result.image_urls" :key="'imgurl-' + idx" class="image-card">
          <img :src="apiUrl(url)" :alt="'配图 ' + (idx + 1)" class="preview-img" loading="lazy" />
          <figcaption class="image-cap">配图 {{ idx + 1 }}</figcaption>
        </figure>
      </div>
    </section>

    <section class="card">
      <div class="block-head">
        <h2 class="block-title">发布建议</h2>
        <button type="button" class="copy-btn" @click="copyLines(result?.publish_tips, 'publish_tips')">复制</button>
      </div>
      <p v-if="!result" class="empty">点击「生成内容」后显示</p>
      <p v-else-if="!result.publish_tips?.length" class="empty">暂无结果</p>
      <p v-for="(item, idx) in result?.publish_tips || []" :key="'tip-' + idx" class="item">• {{ item }}</p>
    </section>

    <section class="card">
      <div class="block-head">
        <h2 class="block-title">风险 / 注意事项</h2>
        <button type="button" class="copy-btn" @click="copyLines(result?.risks, 'risks')">复制</button>
      </div>
      <p v-if="!result" class="empty">点击「生成内容」后显示</p>
      <p v-else-if="!result.risks?.length" class="empty">暂无结果</p>
      <p v-for="(item, idx) in result?.risks || []" :key="'risk-' + idx" class="item">• {{ item }}</p>
    </section>

    <div v-if="toast" class="toast" role="status">{{ toast }}</div>
    <ErrorDialog v-model="errorDialog" :text="errorText" />
  </div>
</template>

<style scoped>
.page {
  max-width: 760px;
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
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-radius: var(--radius, 18px);
  padding: 18px 16px;
  margin-bottom: 14px;
  border: var(--border-soft, 1px solid rgba(148, 163, 184, 0.22));
  box-shadow: var(--shadow-card, 0 4px 24px rgba(15, 23, 42, 0.06));
}

.header {
  padding-top: 20px;
}

.title-wrap {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.title-accent {
  width: 4px;
  min-height: 56px;
  border-radius: 999px;
  background: linear-gradient(180deg, #6366f1, #a855f7, #06b6d4);
}

.title {
  margin: 0 0 8px;
  font-size: 22px;
  font-weight: 800;
  line-height: 1.3;
  letter-spacing: -0.02em;
  color: #0f172a;
}

.sub {
  margin: 0;
  color: #64748b;
  font-size: 14px;
  line-height: 1.6;
}

.grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
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

.input:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.45);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.progress-wrap {
  margin-top: 12px;
}

.progress-bar {
  height: 6px;
  border-radius: 999px;
  background: rgba(148, 163, 184, 0.25);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #6366f1, #8b5cf6);
  transition: width 0.35s ease;
}

.progress-hint {
  margin: 8px 0 0;
  font-size: 13px;
  color: #64748b;
}

.btn {
  width: 100%;
  margin-top: 14px;
  padding: 14px 16px;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 600;
}

.block-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 10px;
}

.block-title {
  margin: 0;
  font-size: 15px;
  font-weight: 700;
  color: #0f172a;
}

.copy-btn {
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(255, 255, 255, 0.95);
  color: #4338ca;
  font-size: 13px;
  font-weight: 600;
  border-radius: 10px;
  padding: 6px 10px;
}

.empty {
  margin: 0;
  color: #94a3b8;
  font-size: 14px;
}

.item {
  margin: 0 0 8px;
  color: #334155;
  font-size: 14px;
  line-height: 1.6;
}

.item:last-child {
  margin-bottom: 0;
}

.field-check {
  flex-direction: row;
  align-items: flex-start;
  gap: 10px;
  grid-column: 1 / -1;
}

.checkbox {
  margin-top: 4px;
  width: 16px;
  height: 16px;
  flex-shrink: 0;
}

.label-inline {
  font-size: 13px;
  line-height: 1.5;
  color: #475569;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
  gap: 12px;
}

.image-card {
  margin: 0;
}

.preview-img {
  width: 100%;
  aspect-ratio: 3 / 4;
  object-fit: cover;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: #f1f5f9;
}

.image-cap {
  margin-top: 6px;
  font-size: 12px;
  color: #64748b;
  text-align: center;
}

.text-block {
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 14px;
  line-height: 1.7;
  color: #1e293b;
  background: linear-gradient(135deg, rgba(241, 245, 249, 0.95), rgba(238, 242, 255, 0.9));
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 14px;
  padding: 12px;
}

.toast {
  position: fixed;
  left: 50%;
  bottom: 48px;
  transform: translateX(-50%);
  padding: 12px 20px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.88);
  color: #fff;
  font-size: 14px;
  z-index: 2000;
  max-width: 90vw;
  text-align: center;
}
</style>
