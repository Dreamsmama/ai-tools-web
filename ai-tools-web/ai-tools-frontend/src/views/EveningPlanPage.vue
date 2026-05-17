<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import EveningPlanForm from '../components/eveningPlan/EveningPlanForm.vue'
import EveningPlanResult from '../components/eveningPlan/EveningPlanResult.vue'
import ErrorDialog from '../components/ErrorDialog.vue'
import {
  BUDGET_OPTIONS,
  ENERGY_OPTIONS,
  GO_OUT_OPTIONS,
  INTEREST_OPTIONS,
  MOOD_OPTIONS,
  SOCIAL_OPTIONS,
} from '../data/eveningPlanOptions.js'
import { requestEveningPlan } from '../lib/eveningPlanApi.js'
import { trackApiFail, trackApiSuccess, trackEvent, trackSubmit } from '../analytics.js'

const PAGE_PATH = '/tools/evening-plan'
const FEATURE = 'evening_plan'

function defaultTime() {
  const d = new Date()
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function createDefaultForm() {
  return {
    city: '',
    current_time: defaultTime(),
    energy_level: ENERGY_OPTIONS[0],
    mood: MOOD_OPTIONS[0],
    go_out: GO_OUT_OPTIONS[0],
    social: SOCIAL_OPTIONS[0],
    budget: BUDGET_OPTIONS[1],
    interests: [],
    extra_notes: '',
  }
}

const phase = ref(/** @type {'form'|'result'} */ ('form'))
const form = ref(createDefaultForm())
const loading = ref(false)
/** @type {import('vue').Ref<object|null>} */
const result = ref(null)
const toast = ref('')
const errorDialog = ref(false)
const errorText = ref('')

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

function validateForm() {
  if (!(form.value.city || '').trim()) {
    showErrorDetail('请填写当前城市，方便推荐附近可搜的类型。')
    return false
  }
  if (!form.value.interests?.length) {
    showErrorDetail('请至少选一项「今天更想做什么」。')
    return false
  }
  return true
}

async function generatePlan() {
  if (!validateForm()) return

  loading.value = true
  const requestStart = Date.now()
  const trackEventId = trackSubmit(FEATURE, PAGE_PATH)
  trackEvent('evening_plan_submit', {
    feature: FEATURE,
    page: PAGE_PATH,
    event_id: trackEventId,
  })

  const payload = {
    city: form.value.city.trim(),
    current_time: form.value.current_time,
    energy_level: form.value.energy_level,
    mood: form.value.mood,
    go_out: form.value.go_out,
    social: form.value.social,
    budget: form.value.budget,
    interests: [...form.value.interests],
    extra_notes: (form.value.extra_notes || '').trim(),
  }

  const res = await requestEveningPlan(payload)

  if (!res.ok) {
    trackApiFail(FEATURE, PAGE_PATH, trackEventId, res.kind, Date.now() - requestStart)
    showErrorDetail(res.message)
    loading.value = false
    return
  }

  trackApiSuccess(FEATURE, PAGE_PATH, trackEventId, Date.now() - requestStart)
  result.value = res.data
  phase.value = 'result'
  loading.value = false
  trackEvent('evening_plan_result_view', {
    feature: FEATURE,
    page: PAGE_PATH,
    event_id: trackEventId,
  })
}

function editConditions() {
  phase.value = 'form'
  trackEvent('evening_plan_edit', { feature: FEATURE, page: PAGE_PATH })
}

function formatResultText(data) {
  const lines = [
    '【今晚推荐模式】',
    data.mode || '',
    '',
    '【适合你的今晚安排】',
  ]

  ;(data.plans || []).forEach((plan, idx) => {
    const label = plan.plan_type || ['方案一：吃什么', '方案二：做什么', '方案三：回家后怎么收尾'][idx]
    lines.push(`\n${label}`)
    if (plan.title) lines.push(`标题：${plan.title}`)
    if (plan.reason) lines.push(`推荐理由：${plan.reason}`)
    if (plan.actions?.length) {
      lines.push('具体行动：')
      plan.actions.forEach((a) => lines.push(`  - ${a}`))
    }
    if (plan.cost) lines.push(`预计花费：${plan.cost}`)
    if (plan.duration) lines.push(`预计耗时：${plan.duration}`)
    if (plan.fit_score) lines.push(`适合程度：${plan.fit_score}/5`)
  })

  if (data.avoid?.length) {
    lines.push('', '【不建议你今晚做什么】')
    data.avoid.forEach((x) => lines.push(`- ${x}`))
  }

  if (data.lazy_fallback) {
    lines.push('', '【如果你只想躺平】')
    if (data.lazy_fallback.title) lines.push(data.lazy_fallback.title)
    lines.push(data.lazy_fallback.description || '')
  }

  if (data.tomorrow_tips?.length) {
    lines.push('', '【明天状态保护建议】')
    data.tomorrow_tips.forEach((x) => lines.push(`- ${x}`))
  }

  return lines.filter((l) => l !== undefined).join('\n')
}

async function copyResult() {
  if (!result.value) return
  try {
    await navigator.clipboard.writeText(formatResultText(result.value))
    trackEvent('evening_plan_copy', { feature: FEATURE, page: PAGE_PATH })
    showToast('已复制今晚安排')
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

    <header class="hero card">
      <h1 class="title">下班后不知道干什么？</h1>
      <p class="sub">输入你现在的状态，让 AI 给你安排一个不内耗的晚上。</p>
    </header>

    <template v-if="phase === 'form'">
      <EveningPlanForm v-model="form" :loading="loading" @submit="generatePlan" />
    </template>

    <template v-else-if="result">
      <div class="result-wrap" :class="{ 'result-wrap--loading': loading }">
        <p v-if="loading" class="loading-hint" role="status">正在根据你的状态安排今晚...</p>
        <EveningPlanResult
          v-show="!loading"
          :result="result"
          @regenerate="generatePlan"
          @edit="editConditions"
          @copy="copyResult"
        />
      </div>
    </template>

    <div v-if="toast" class="toast" role="status">{{ toast }}</div>
    <ErrorDialog v-model="errorDialog" :text="errorText" />
  </div>
</template>

<style scoped>
.page {
  max-width: 520px;
  margin: 0 auto;
  padding: 16px 14px 48px;
  min-height: 100vh;
}

.top-nav {
  padding: 0 2px 12px;
}

.nav-link {
  font-size: 14px;
  font-weight: 600;
  color: #6366f1;
  text-decoration: none;
}

.hero {
  margin-bottom: 16px;
}

.card {
  background: var(--surface-solid);
  border-radius: var(--radius);
  padding: 18px 16px;
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
}

.title {
  margin: 0 0 8px;
  font-size: 22px;
  font-weight: 800;
  color: var(--text);
  line-height: 1.35;
}

.sub {
  margin: 0;
  font-size: 14px;
  line-height: 1.65;
  color: var(--text-muted);
}

.result-wrap--loading {
  min-height: 200px;
}

.loading-hint {
  margin: 24px 0;
  text-align: center;
  font-size: 15px;
  font-weight: 600;
  color: #6366f1;
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
}
</style>
