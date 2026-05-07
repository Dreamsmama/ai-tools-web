<script setup>
import { onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { API, apiUrl, logApiFailure } from '../api.js'
import { trackApiFail, trackApiSuccess, trackEvent, trackSubmit } from '../analytics.js'
import { httpErrorMessage, NETWORK_UNREACHABLE, RESPONSE_PARSE_ERROR } from '../clientErrors.js'
import ErrorDialog from '../components/ErrorDialog.vue'

const PAGE_PATH = '/tools/offer-decision'
const FEATURE = 'offer_decision'
const USE_COUNT_KEY = 'offer_analysis_use_count'

const inputText = ref('')
const loading = ref(false)
const result = ref(null)
const toast = ref('')
const errorDialog = ref(false)
const errorText = ref('')
const exampleInput = `我现在有三个选择，特别纠结：
1）留在当前公司：业务稳定，薪资一般，技术偏传统；
2）去一家AI创业公司：薪资高一些，但节奏快、方向可能变；
3）回学校读博：长期看研究深度更强，但短期收入下降，时间成本高。

我目前最在意的是长期竞争力，但也担心生活稳定性和家里压力。`

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

function detectCaseTypes(text) {
  const t = String(text || '')
  const types = []
  if (/(ai|大模型|算法|转型|转岗|方向)/i.test(t)) types.push('AI转型')
  if (/(稳定|裁员|风险|大厂|国企|编制)/.test(t)) types.push('稳定性')
  if (/(薪资|工资|总包|涨薪|期权|股票|奖金)/.test(t)) types.push('薪资')
  if (/(城市|落户|通勤|异地|搬家|租房)/.test(t)) types.push('城市')
  if (/(团队|老板|leader|管理|汇报|文化|氛围)/i.test(t)) types.push('团队')
  return types.length ? types : ['未分类']
}

function currentUseCount() {
  try {
    return parseInt(localStorage.getItem(USE_COUNT_KEY) || '0', 10) || 0
  } catch {
    return 0
  }
}

function increaseUseCount() {
  try {
    localStorage.setItem(USE_COUNT_KEY, String(currentUseCount() + 1))
  } catch {
    /* ignore */
  }
}

onMounted(() => {
  if (currentUseCount() >= 1) {
    trackEvent('offer_analysis_second_use', { feature: FEATURE, page: PAGE_PATH })
  }
})

async function onAnalyze() {
  const text = (inputText.value || '').trim()
  if (!text) {
    showErrorDetail('请先填写你的职业选择和顾虑。')
    return
  }

  const caseTypes = detectCaseTypes(text)
  caseTypes.forEach((caseType) => {
    trackEvent('offer_case_type', {
      feature: FEATURE,
      page: PAGE_PATH,
      props: { case_type: caseType },
    })
  })

  loading.value = true
  const requestStart = Date.now()
  const trackEventId = trackSubmit(FEATURE, PAGE_PATH)
  trackEvent('offer_analysis_submit', {
    feature: FEATURE,
    page: PAGE_PATH,
    event_id: trackEventId,
  })
  const url = apiUrl(API.offerDecision)
  const requestBody = { input_text: text }

  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    })

    if (!res.ok) {
      await logApiFailure(url, requestBody, res, new Error(`HTTP ${res.status}`))
      trackApiFail(FEATURE, PAGE_PATH, trackEventId, `http_${res.status}`, Date.now() - requestStart)
      showErrorDetail(httpErrorMessage(res.status))
      return
    }

    let payload
    try {
      payload = await res.json()
    } catch (parseErr) {
      await logApiFailure(url, requestBody, res, parseErr)
      trackApiFail(FEATURE, PAGE_PATH, trackEventId, 'response_parse_error', Date.now() - requestStart)
      showErrorDetail(RESPONSE_PARSE_ERROR)
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
      showErrorDetail(payload?.message || '分析失败，请稍后再试。')
      return
    }

    trackApiSuccess(FEATURE, PAGE_PATH, trackEventId, Date.now() - requestStart)
    result.value = payload.data
    increaseUseCount()
    trackEvent('offer_analysis_result_view', {
      feature: FEATURE,
      page: PAGE_PATH,
      event_id: trackEventId,
    })
  } catch (err) {
    await logApiFailure(url, requestBody, null, err)
    trackApiFail(FEATURE, PAGE_PATH, trackEventId, 'network_error', Date.now() - requestStart)
    showErrorDetail(NETWORK_UNREACHABLE)
  } finally {
    loading.value = false
  }
}

async function copyResult() {
  if (!result.value) return
  const text = [
    '【你现在真正纠结的核心】',
    ...(result.value.core_conflict || []),
    '',
    '【每个选择的核心特点】',
    ...((result.value.option_insights || []).flatMap((opt) => [
      `${opt.option_name || '未命名选择'}`,
      `稳定性：${opt.stability || '暂无'}`,
      `成长性：${opt.growth || '暂无'}`,
      `风险：${opt.risk || '暂无'}`,
      `长期空间：${opt.long_term_space || '暂无'}`,
      `技术价值：${opt.tech_value || '暂无'}`,
      `团队/行业因素：${opt.team_industry_factor || '暂无'}`,
      '',
    ]) || []),
    '',
    '【你现在最容易忽略的问题】',
    ...(result.value.blind_spots || []),
    '',
    '【3个月后可能后悔的点】',
    ...(result.value.regret_after_3_months || []),
    '',
    '【什么样的人更适合不同选择】',
    ...(result.value.fit_by_choice || []),
    '',
    '【建议你继续确认的问题】',
    ...(result.value.questions_to_confirm || []),
    '',
    '【建议】',
    result.value.recommendation || '',
  ]
    .map((v) => (v ? `- ${v}` : ''))
    .join('\n')
    .replace(/^- 【/gm, '【')

  try {
    await navigator.clipboard.writeText(text)
    trackEvent('offer_analysis_copy', { feature: FEATURE, page: PAGE_PATH })
    showToast('已复制分析内容')
  } catch {
    showToast('复制失败，请手动复制')
  }
}
</script>

<template>
  <div class="page">
    <nav class="top-nav">
      <RouterLink class="nav-link" to="/">← 首页</RouterLink>
    </nav>

    <section class="card header">
      <h1 class="title">职业决策辅助</h1>
      <p class="sub">不是给你打分，而是帮你把选择焦虑拆清楚。</p>
    </section>

    <section class="card">
      <div class="label">输入你的职业选择和顾虑</div>
      <textarea
        v-model="inputText"
        class="textarea"
        rows="10"
        placeholder="例如：&#10;我现在在纠结两个offer / 读博 / 考公 / 创业，&#10;最怕选错后3个月后悔……&#10;可以把聊天记录和顾虑一起贴上来。"
      />
      <button type="button" class="textBtn" @click="inputText = exampleInput">填入示例</button>
      <button type="button" class="btn btn-gradient" :disabled="loading" @click="onAnalyze">
        {{ loading ? '分析中…' : '帮我分析' }}
      </button>
    </section>

    <section class="card">
      <h2 class="block-title">你现在真正纠结的核心</h2>
      <p v-if="!result" class="empty">点击「帮我分析」后显示</p>
      <p v-for="(item, idx) in result?.core_conflict || []" :key="`a-${idx}`" class="item">• {{ item }}</p>
    </section>

    <section class="card">
      <h2 class="block-title">每个选择的核心特点</h2>
      <p v-if="!result" class="empty">点击「帮我分析」后显示</p>
      <div v-for="(opt, idx) in result?.option_insights || []" :key="`opt-${idx}`" class="optionBox">
        <h3 class="optionTitle">{{ opt.option_name || `选择 ${idx + 1}` }}</h3>
        <p class="item">• 稳定性：{{ opt.stability || '暂无' }}</p>
        <p class="item">• 成长性：{{ opt.growth || '暂无' }}</p>
        <p class="item">• 风险：{{ opt.risk || '暂无' }}</p>
        <p class="item">• 长期空间：{{ opt.long_term_space || '暂无' }}</p>
        <p class="item">• 技术价值：{{ opt.tech_value || '暂无' }}</p>
        <p class="item">• 团队/行业因素：{{ opt.team_industry_factor || '暂无' }}</p>
      </div>
    </section>

    <section class="card">
      <h2 class="block-title">你现在最容易忽略的问题</h2>
      <p v-if="!result" class="empty">点击「帮我分析」后显示</p>
      <p v-for="(item, idx) in result?.blind_spots || []" :key="`d-${idx}`" class="item">• {{ item }}</p>
    </section>

    <section class="card">
      <h2 class="block-title">3个月后可能后悔的点</h2>
      <p v-if="!result" class="empty">点击「帮我分析」后显示</p>
      <p v-for="(item, idx) in result?.regret_after_3_months || []" :key="`e-${idx}`" class="item">• {{ item }}</p>
    </section>

    <section class="card">
      <h2 class="block-title">什么样的人更适合不同选择</h2>
      <p v-if="!result" class="empty">点击「帮我分析」后显示</p>
      <p v-for="(item, idx) in result?.fit_by_choice || []" :key="`f-${idx}`" class="item">• {{ item }}</p>
    </section>

    <section class="card">
      <h2 class="block-title">建议你继续确认的问题</h2>
      <p v-if="!result" class="empty">点击「帮我分析」后显示</p>
      <p v-for="(item, idx) in result?.questions_to_confirm || []" :key="`g-${idx}`" class="item">• {{ item }}</p>
    </section>

    <section class="card">
      <h2 class="block-title">建议</h2>
      <p v-if="!result" class="empty">点击「帮我分析」后显示</p>
      <div v-else class="reply">{{ result.recommendation || '暂无建议' }}</div>
      <button v-if="result" type="button" class="copyBtn" @click="copyResult">复制分析</button>
    </section>

    <div v-if="toast" class="toast" role="status">{{ toast }}</div>
    <ErrorDialog v-model="errorDialog" :text="errorText" />
  </div>
</template>

<style scoped>
.page { max-width: 760px; margin: 0 auto; padding: 16px 12px 40px; min-height: 100vh; }
.top-nav { padding: 0 4px 12px; }
.nav-link { font-size: 14px; font-weight: 500; color: #6366f1; text-decoration: none; }
.card { background: rgba(255, 255, 255, 0.9); border-radius: 18px; padding: 18px 16px; margin-bottom: 14px; border: 1px solid rgba(148, 163, 184, 0.22); box-shadow: 0 4px 24px rgba(15, 23, 42, 0.06); }
.title { margin: 0 0 8px; font-size: 22px; font-weight: 800; color: #0f172a; }
.sub { margin: 0; color: #64748b; font-size: 14px; line-height: 1.6; }
.label { font-size: 13px; font-weight: 600; color: #475569; margin-bottom: 10px; }
.textarea { width: 100%; min-height: 160px; padding: 14px; border-radius: 14px; background: rgba(241, 245, 249, 0.9); border: 1px solid rgba(148, 163, 184, 0.22); font-size: 15px; line-height: 1.55; resize: vertical; }
.textarea:focus { outline: none; border-color: rgba(99, 102, 241, 0.45); box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15); }
.textBtn { margin-top: 8px; border: none; background: transparent; color: #4f46e5; font-size: 13px; padding: 0; }
.btn { width: 100%; margin-top: 12px; padding: 14px 16px; border-radius: 14px; font-size: 16px; font-weight: 600; }
.block-title { font-size: 15px; font-weight: 700; margin: 0 0 12px; color: #0f172a; }
.empty { margin: 0; font-size: 14px; color: #94a3b8; }
.item { margin: 0 0 10px; color: #334155; font-size: 15px; line-height: 1.6; }
.item:last-child { margin-bottom: 0; }
.optionBox { border: 1px solid rgba(148, 163, 184, 0.22); border-radius: 12px; padding: 12px; margin-bottom: 10px; background: rgba(248, 250, 252, 0.8); }
.optionTitle { margin: 0 0 8px; font-size: 15px; font-weight: 700; color: #0f172a; }
.reply { font-size: 15px; color: #1e293b; line-height: 1.65; padding: 14px; border-radius: 14px; background: rgba(241, 245, 249, 0.9); border: 1px solid rgba(148, 163, 184, 0.22); white-space: pre-wrap; word-break: break-word; }
.copyBtn { width: 100%; margin-top: 12px; padding: 12px 14px; border-radius: 12px; border: 1px solid rgba(148, 163, 184, 0.35); background: rgba(255, 255, 255, 0.95); color: #4338ca; font-size: 15px; font-weight: 600; }
.toast { position: fixed; left: 50%; bottom: 48px; transform: translateX(-50%); padding: 12px 20px; border-radius: 999px; background: rgba(15, 23, 42, 0.88); color: #fff; font-size: 14px; z-index: 2000; }
</style>
