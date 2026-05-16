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
  work_reply: '职场沟通理解 + 回复生成',
  summary: '职场沟通理解 + 回复生成（旧埋点）',
  medical: '就医前沟通准备',
  offer_decision: 'Offer / 职业决策辅助',
  rag_upload_ask: 'RAG 上传后提问',
  rag_official_ask: 'RAG 官方模板提问',
  career_test: '职业倾向测试',
  career_library: '职业观察库',
  career: '职业规划（首页 Hero）',
  career_experience: 'AI 职业体验馆 / 打工人格实验室',
  xiaohongshu_agent: '小红书内容生产 Agent',
  model_compare: '模型优化实验 / 对比',
  memory_compare: 'AI 记忆对比',
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

/** 自定义 trackEvent 的 event 名 → 中文说明（便于看板阅读） */
const eventLabelMap = {
  page_view: '页面浏览',
  submit_click: '提交点击',
  api_success: '接口成功',
  api_fail: '接口失败',
  career_hero_test_click: '职业规划·Hero 点「开始职业测试」',
  career_hero_library_click: '职业规划·Hero 点「职业观察库」',
  career_hero_experience_click: '职业规划·Hero 点「AI 职业体验馆」',
  career_test_result: '职业测试·生成结果',
  career_test_restart: '职业测试·重新测试',
  career_recommend_detail_click: '职业测试·从推荐进详情',
  career_result_library_click: '职业测试·结果页进观察库',
  career_library_view: '职业观察库·进入页面',
  career_library_card_click: '职业观察库·点职业卡片',
  career_library_to_test_click: '职业观察库·去做测试',
  career_detail_view: '职业详情·查看',
  career_experience_hub_view: '打工人格实验室·进入首页',
  career_experience_pick: '打工人格实验室·选择剧集',
  career_experience_start: '打工人格实验室·开始追剧',
  career_experience_complete: '打工人格实验室·看完一集',
  career_experience_share_save_click: '打工人格实验室·点击保存打工人格',
  career_experience_share_save_success: '打工人格实验室·保存打工人格成功',
  career_experience_share_save_fail: '打工人格实验室·保存打工人格失败',
  offer_analysis_submit: 'Offer 分析·提交',
  offer_analysis_result_view: 'Offer 分析·查看结果',
  offer_analysis_copy: 'Offer 分析·复制',
  offer_analysis_second_use: 'Offer 分析·二次使用',
  offer_case_type: 'Offer 分析·案例类型',
}

function eventLabel(raw) {
  if (!raw) return '未知'
  return eventLabelMap[raw] || raw
}

const summary = computed(() => data.value?.summary || {})
const featureUsage = computed(() => data.value?.feature_usage || [])
const eventBreakdown = computed(() => data.value?.event_breakdown || [])
const pageViewsByPath = computed(() => data.value?.page_views_by_path || [])
const trend = computed(() => data.value?.trend || [])
const recentFailures = computed(() => data.value?.recent_failures || [])
const rangeText = computed(() => {
  const r = data.value?.range
  if (!r) return '-'
  return `${r.start_date} 至 ${r.end_date}`
})

/** 接口成功但区间内没有任何埋点事件（常见于反代未转发或库表为空） */
const showZeroDataHint = computed(() => {
  const s = data.value?.summary
  if (!s) return false
  return (Number(s.total_events) || 0) === 0
})

function countEventInBreakdown(events, eventName) {
  const row = events.find((e) => e.event === eventName)
  return row ? Number(row.count) || 0 : 0
}

/**
 * 功能使用排行：在原有 submit_click 按 feature 聚合之上，
 * 置顶职业模块的关键自定义事件，避免非接口型互动功能在排行中显示为 0。
 */
const mergedFeatureRanking = computed(() => {
  if (!data.value) return []
  const bd = eventBreakdown.value
  const fu = featureUsage.value
  const heroClicks =
    countEventInBreakdown(bd, 'career_hero_test_click') +
    countEventInBreakdown(bd, 'career_hero_library_click')
  const careerSubmit = fu.find((x) => x.feature === 'career_test')?.count ?? 0
  const careerExperienceStarts = countEventInBreakdown(bd, 'career_experience_start')
  const careerExperienceShareClicks = countEventInBreakdown(bd, 'career_experience_share_save_click')
  const careerExperienceShareSuccess = countEventInBreakdown(bd, 'career_experience_share_save_success')

  const rows = [
    {
      key: '_ai_career_platform',
      title: 'AI 职业成长平台',
      subtitle:
        '首页 Hero：开始职业测试 + 查看职业观察库（点击次数，来自埋点事件 career_hero_*；无「事件分布」数据时可能为 0）',
      count: heroClicks,
    },
    {
      key: '_ai_career_test',
      title: 'AI 时代，你适合什么样的工作？',
      subtitle:
        '职业倾向测试：卷末「提交并查看结果」次数（submit_click，feature=career_test）',
      count: Number(careerSubmit) || 0,
    },
    {
      key: '_ai_career_experience',
      title: 'AI 职业体验馆 / 打工人格实验室',
      subtitle: '职业互动体验：「开始上班/追剧」次数（来自埋点事件 career_experience_start）',
      count: careerExperienceStarts,
    },
    {
      key: '_ai_career_experience_share',
      title: '打工人格实验室·保存打工人格',
      subtitle: `结局页「保存我的打工人格」点击次数；成功生成 ${careerExperienceShareSuccess} 次`,
      count: careerExperienceShareClicks,
    },
  ]

  for (const item of fu) {
    if (item.feature === 'career_test') continue
    rows.push({
      key: item.feature,
      title: featureLabel(item.feature),
      subtitle: '',
      count: Number(item.count) || 0,
    })
  }
  return rows
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
      <p class="sub">
        说明：独立用户按 IP 去重；成功率 = 接口成功次数 / 提交点击次数。「功能使用排行」只含带提交的功能；浏览与职业规划等自定义事件见下方「埋点事件分布」。
      </p>
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
      <div v-if="showZeroDataHint" class="zero-hint" role="note">
        <p class="zero-hint-title">当前区间总事件数为 0，常见原因如下：</p>
        <ul class="zero-hint-list">
          <li>
            <strong>反代路径：</strong>前端请求的是 <code>/api/track/stats</code> 与
            <code>/api/track/events</code>，后端实际路由为 <code>/track/stats</code>、
            <code>/track/events</code>。Nginx 需把前缀 <code>/api</code> 去掉再转发（与本地 Vite
            proxy 一致），例如：
            <code class="zero-hint-code">location /api/track/ { proxy_pass http://127.0.0.1:8000/track/; }</code>
          </li>
          <li><strong>数据库：</strong>埋点写入 PostgreSQL（<code>ANALYTICS_DATABASE_URL</code> 未配时用 <code>RAG_DATABASE_URL</code>）。库连不上时接口会报错而非全 0。</li>
          <li><strong>区间：</strong>可切换「全部时间」或拉大日期范围，排除时区/日期边界导致查不到数据。</li>
          <li><strong>尚未产生数据：</strong>需有用户访问页面（<code>page_view</code>）或使用带提交的功能后才会出现非零统计。</li>
        </ul>
      </div>
    </section>

    <section class="card">
      <h2 class="block-title">功能使用排行</h2>
      <p class="hint-inline">
        前几行为职业模块：职业成长平台与打工人格实验室来自自定义事件汇总；职业测试来自
        <code>submit_click</code>。其余行仍为各功能的提交次数（与旧版排行一致）。
      </p>
      <p v-if="!data" class="empty">请先加载统计</p>
      <p v-else-if="mergedFeatureRanking.length === 0" class="empty">当前区间暂无数据</p>
      <div v-else class="list">
        <div v-for="item in mergedFeatureRanking" :key="item.key" class="list-row">
          <span class="rank-cell">
            <span class="rank-title">{{ item.title }}</span>
            <span v-if="item.subtitle" class="rank-sub">{{ item.subtitle }}</span>
          </span>
          <strong>{{ item.count }}</strong>
        </div>
      </div>
    </section>

    <section class="card">
      <h2 class="block-title">埋点事件分布</h2>
      <p class="hint-inline">按事件名汇总（含页面浏览、提交、接口结果及职业规划等自定义事件）。老版本接口无此块时为空。</p>
      <p v-if="eventBreakdown.length === 0" class="empty">暂无事件分布数据</p>
      <div v-else class="list">
        <div v-for="item in eventBreakdown" :key="item.event" class="list-row">
          <span class="event-cell">
            <span class="event-name">{{ eventLabel(item.event) }}</span>
            <code class="event-raw">{{ item.event }}</code>
          </span>
          <strong>{{ item.count }}</strong>
        </div>
      </div>
    </section>

    <section class="card">
      <h2 class="block-title">页面浏览 Top</h2>
      <p class="hint-inline">仅 <code>page_view</code>，按路径聚合，便于看哪些路由被打开最多。</p>
      <p v-if="pageViewsByPath.length === 0" class="empty">暂无页面浏览数据</p>
      <div v-else class="list">
        <div v-for="item in pageViewsByPath" :key="item.page" class="list-row">
          <span class="page-path">{{ item.page || '/' }}</span>
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
.sub { margin: 0; color: #64748b; font-size: 14px; line-height: 1.55; }
.hint-inline {
  margin: 0 0 12px;
  font-size: 13px;
  color: #64748b;
  line-height: 1.55;
}
.hint-inline code {
  font-size: 12px;
  padding: 1px 5px;
  border-radius: 4px;
  background: #f1f5f9;
}
.event-cell {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 2px;
  min-width: 0;
}
.event-name {
  font-size: 14px;
  color: #334155;
}
.event-raw {
  font-size: 11px;
  color: #94a3b8;
  word-break: break-all;
  background: transparent;
  border: none;
  padding: 0;
}
.page-path {
  font-size: 13px;
  word-break: break-all;
  color: #334155;
}
.rank-cell {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  min-width: 0;
  padding-right: 8px;
}
.rank-title {
  font-size: 14px;
  font-weight: 600;
  color: #0f172a;
  line-height: 1.35;
}
.rank-sub {
  font-size: 12px;
  line-height: 1.45;
  color: #64748b;
}
.block-title { font-size: 15px; font-weight: 700; margin: 0 0 12px; color: #0f172a; }
.filters { display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 10px; margin-bottom: 10px; }
.field { display: flex; flex-direction: column; gap: 6px; font-size: 12px; color: #475569; }
.input { width: 100%; border-radius: 12px; border: 1px solid rgba(148,163,184,.3); background: #f8fafc; color: #0f172a; padding: 10px 12px; }
.btn { width: 100%; padding: 12px 14px; border-radius: 12px; font-size: 14px; font-weight: 600; }
.meta { margin: 10px 0 0; font-size: 12px; color: #64748b; }
.zero-hint {
  margin-top: 14px;
  padding: 12px 14px;
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(238, 242, 255, 0.9), rgba(250, 245, 255, 0.85));
  border: 1px solid rgba(99, 102, 241, 0.22);
  font-size: 13px;
  line-height: 1.65;
  color: #334155;
}
.zero-hint-title { margin: 0 0 8px; font-weight: 700; color: #4338ca; }
.zero-hint-list { margin: 0; padding-left: 1.15rem; }
.zero-hint-list li { margin-bottom: 8px; }
.zero-hint-list li:last-child { margin-bottom: 0; }
.zero-hint code {
  font-size: 12px;
  padding: 2px 6px;
  border-radius: 6px;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(148, 163, 184, 0.35);
  word-break: break-all;
}
.zero-hint-code { display: block; margin-top: 6px; white-space: pre-wrap; }
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
