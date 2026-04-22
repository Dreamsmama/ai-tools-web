<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { API, apiUrl, logApiFailure } from '../api.js'
import { httpErrorMessage, NETWORK_UNREACHABLE, RESPONSE_PARSE_ERROR } from '../clientErrors.js'
import ErrorDialog from '../components/ErrorDialog.vue'

const period = ref('7d')
const startDate = ref('')
const endDate = ref('')
const loading = ref(false)
const data = ref(null)
const errorDialog = ref(false)
const errorText = ref('')

const periodOptions = [
  { value: 'today', label: '今天' },
  { value: '7d', label: '最近 7 天' },
  { value: '30d', label: '最近 30 天' },
  { value: 'all', label: '全部时间' },
]

const featureLabelMap = {
  summary: '聊天重点总结',
  medical: '就医前沟通准备',
  rag_upload_ask: 'RAG 上传后提问',
  rag_official_ask: 'RAG 官方模板提问',
  unknown: '未分类',
}

const errorLabelMap = {
  network_error: '网络异常',
  response_parse_error: '返回解析失败',
  business_error: '业务失败',
  unknown: '未知异常',
}

function showErrorDetail(text) {
  errorText.value = text
  errorDialog.value = true
}

function featureLabel(raw) {
  return featureLabelMap[raw] || raw || '未分类'
}

function errorLabel(raw) {
  if (!raw) return '未知异常'
  if (errorLabelMap[raw]) return errorLabelMap[raw]
  if (raw.startsWith('http_')) return `HTTP ${raw.replace('http_', '')}`
  if (raw.startsWith('business_')) return `业务码 ${raw.replace('business_', '')}`
  return raw
}

const summary = computed(() => data.value?.summary || {})
const featureUsage = computed(() => data.value?.feature_usage || [])
const trend = computed(() => data.value?.trend || [])
const recentFailures = computed(() => data.value?.recent_failures || [])
const rangeText = computed(() => {
  const r = data.value?.range
  if (!r) return '-'
  return `${r.start_date} 至 ${r.end_date}`
})

async function loadStats() {
  loading.value = true
  const params = new URLSearchParams()
  params.set('period', period.value)
  if (startDate.value) params.set('start_date', startDate.value)
  if (endDate.value) params.set('end_date', endDate.value)
  const url = `${apiUrl(API.trackStats)}?${params.toString()}`
  try {
    const res = await fetch(url)
    if (!res.ok) {
      await logApiFailure(url, null, res, new Error(`HTTP ${res.status}`))
      showErrorDetail(httpErrorMessage(res.status))
      return
    }
    let payload
    try {
      payload = await res.json()
    } catch (parseErr) {
      await logApiFailure(url, null, res, parseErr)
      showErrorDetail(RESPONSE_PARSE_ERROR)
      return
    }
    if (!payload || payload.code !== 0 || !payload.data) {
      showErrorDetail(payload?.message || '统计数据读取失败')
      return
    }
    data.value = payload.data
  } catch (e) {
    await logApiFailure(url, null, null, e)
    showErrorDetail(NETWORK_UNREACHABLE)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadStats()
})
</script>

<template>
  <div class="page">
    <header class="nav">
      <RouterLink class="back" to="/">← 首页</RouterLink>
    </header>

    <section class="card">
      <h1 class="title">用户使用概览</h1>
      <p class="sub">说明：独立用户按 IP 去重；成功率 = 调用成功次数 / 点击提交次数。</p>
    </section>

    <section class="card">
      <h2 class="block-title">统计范围</h2>
      <div class="filters">
        <label class="field">
          <span>时间范围</span>
          <select v-model="period" class="input">
            <option v-for="item in periodOptions" :key="item.value" :value="item.value">{{ item.label }}</option>
          </select>
        </label>
        <label class="field">
          <span>开始日期</span>
          <input v-model="startDate" class="input" type="date" />
        </label>
        <label class="field">
          <span>结束日期</span>
          <input v-model="endDate" class="input" type="date" />
        </label>
      </div>
      <button class="btn btn-gradient" :disabled="loading" @click="loadStats">
        {{ loading ? '加载中…' : '刷新统计' }}
      </button>
      <p class="meta">当前区间：{{ rangeText }}</p>
    </section>

    <section class="card">
      <h2 class="block-title">核心数据</h2>
      <div class="grid">
        <div class="metric">
          <div class="metric-label">独立用户数</div>
          <div class="metric-value">{{ summary.unique_users || 0 }}</div>
        </div>
        <div class="metric">
          <div class="metric-label">总访问次数</div>
          <div class="metric-value">{{ summary.page_views || 0 }}</div>
        </div>
        <div class="metric">
          <div class="metric-label">提交次数</div>
          <div class="metric-value">{{ summary.submit_clicks || 0 }}</div>
        </div>
        <div class="metric">
          <div class="metric-label">成功率</div>
          <div class="metric-value">{{ summary.success_rate || 0 }}%</div>
        </div>
      </div>
      <p class="meta">
        成功 {{ summary.api_success || 0 }} 次 ｜ 失败 {{ summary.api_fail || 0 }} 次
      </p>
    </section>

    <section class="card">
      <h2 class="block-title">功能使用排行</h2>
      <p v-if="featureUsage.length === 0" class="empty">当前区间暂无提交数据</p>
      <div v-else class="list">
        <div v-for="item in featureUsage" :key="item.feature" class="list-row">
          <span>{{ featureLabel(item.feature) }}</span>
          <strong>{{ item.count }}</strong>
        </div>
      </div>
    </section>

    <section class="card">
      <h2 class="block-title">按天趋势</h2>
      <p v-if="trend.length === 0" class="empty">当前区间暂无趋势数据</p>
      <div v-else class="table-wrap">
        <table class="table">
          <thead>
            <tr>
              <th>日期</th>
              <th>独立用户</th>
              <th>提交</th>
              <th>成功</th>
              <th>失败</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in trend" :key="item.date">
              <td>{{ item.date }}</td>
              <td>{{ item.unique_users }}</td>
              <td>{{ item.submit_clicks }}</td>
              <td>{{ item.api_success }}</td>
              <td>{{ item.api_fail }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <section class="card">
      <h2 class="block-title">最近失败记录</h2>
      <p v-if="recentFailures.length === 0" class="empty">当前区间没有失败记录</p>
      <div v-else class="list">
        <div v-for="item in recentFailures" :key="`${item.timestamp_ms}_${item.feature}`" class="list-row stack">
          <span>{{ item.date }} ｜ {{ featureLabel(item.feature) }}</span>
          <span class="muted">{{ errorLabel(item.error_code) }}</span>
        </div>
      </div>
    </section>

    <ErrorDialog v-model="errorDialog" :text="errorText" />
  </div>
</template>

<style scoped>
.page { max-width: 860px; margin: 0 auto; padding: 16px 12px 40px; min-height: 100vh; }
.nav { padding: 4px 4px 14px; }
.back { font-size: 14px; font-weight: 500; color: #6366f1; text-decoration: none; }
.card { background: rgba(255,255,255,.9); border-radius: 18px; padding: 18px 16px; margin-bottom: 14px; border: 1px solid rgba(148,163,184,.22); box-shadow: 0 4px 24px rgba(15,23,42,.06); }
.title { font-size: 21px; font-weight: 800; margin: 0 0 8px; }
.sub { margin: 0; color: #64748b; font-size: 14px; }
.block-title { font-size: 15px; font-weight: 700; margin: 0 0 12px; color: #0f172a; }
.filters { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-bottom: 10px; }
.field { display: flex; flex-direction: column; gap: 6px; font-size: 12px; color: #475569; }
.input { width: 100%; border-radius: 12px; border: 1px solid rgba(148,163,184,.3); background: #f8fafc; color: #0f172a; padding: 10px 12px; }
.btn { width: 100%; padding: 12px 14px; border-radius: 12px; font-size: 14px; font-weight: 600; }
.meta { margin: 10px 0 0; font-size: 12px; color: #64748b; }
.grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 10px; }
.metric { border: 1px solid rgba(148,163,184,.2); border-radius: 12px; background: #f8fafc; padding: 12px; }
.metric-label { font-size: 12px; color: #64748b; margin-bottom: 4px; }
.metric-value { font-size: 22px; font-weight: 700; color: #0f172a; }
.empty { margin: 0; font-size: 14px; color: #94a3b8; }
.list { display: flex; flex-direction: column; gap: 8px; }
.list-row { display: flex; align-items: center; justify-content: space-between; padding: 10px 12px; border-radius: 10px; background: #f8fafc; border: 1px solid rgba(148,163,184,.2); color: #334155; font-size: 14px; }
.stack { display: flex; flex-direction: column; align-items: flex-start; gap: 4px; }
.muted { color: #64748b; font-size: 13px; }
.table-wrap { overflow-x: auto; }
.table { width: 100%; border-collapse: collapse; font-size: 13px; }
.table th, .table td { border-bottom: 1px solid rgba(148,163,184,.2); padding: 8px 6px; text-align: left; }
.table th { color: #475569; font-weight: 600; }
@media (max-width: 800px) {
  .filters { grid-template-columns: 1fr; }
  .grid { grid-template-columns: 1fr; }
}
</style>
