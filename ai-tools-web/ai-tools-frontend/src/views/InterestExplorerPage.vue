<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import InterestExplorerForm from '../components/interestExplorer/InterestExplorerForm.vue'
import InterestExplorerResult from '../components/interestExplorer/InterestExplorerResult.vue'
import ErrorDialog from '../components/ErrorDialog.vue'
import {
  BUDGET_OPTIONS,
  GOAL_OPTIONS,
  LIFE_STAGE_OPTIONS,
  SOCIAL_STYLE_OPTIONS,
  WEEKEND_STATE_OPTIONS,
  WORK_STATE_OPTIONS,
} from '../data/interestExplorerOptions.js'
import { requestInterestExplorer } from '../lib/interestExplorerApi.js'
import { trackApiFail, trackApiSuccess, trackEvent, trackSubmit } from '../analytics.js'

const PAGE_PATH = '/tools/interest-explorer'
const FEATURE = 'interest_explorer'

function createDefaultForm() {
  return {
    life_stage: LIFE_STAGE_OPTIONS[2],
    work_state: WORK_STATE_OPTIONS[1],
    social_style: SOCIAL_STYLE_OPTIONS[1],
    preferences: [],
    budget: BUDGET_OPTIONS[1],
    weekend_state: WEEKEND_STATE_OPTIONS[2],
    goals: [],
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
  if (!form.value.preferences?.length) {
    showErrorDetail('请至少选一项「更喜欢」。')
    return false
  }
  if (!form.value.goals?.length) {
    showErrorDetail('请至少选一项「你最想获得什么」。')
    return false
  }
  return true
}

async function generateResult() {
  if (!validateForm()) return

  loading.value = true
  const requestStart = Date.now()
  const trackEventId = trackSubmit(FEATURE, PAGE_PATH)
  trackEvent('interest_explorer_submit', {
    feature: FEATURE,
    page: PAGE_PATH,
    event_id: trackEventId,
  })

  const payload = {
    life_stage: form.value.life_stage,
    work_state: form.value.work_state,
    social_style: form.value.social_style,
    preferences: [...form.value.preferences],
    budget: form.value.budget,
    weekend_state: form.value.weekend_state,
    goals: [...form.value.goals],
    extra_notes: (form.value.extra_notes || '').trim(),
  }

  const res = await requestInterestExplorer(payload)

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
  trackEvent('interest_explorer_result_view', {
    feature: FEATURE,
    page: PAGE_PATH,
    event_id: trackEventId,
  })
}

function editConditions() {
  phase.value = 'form'
  trackEvent('interest_explorer_edit', { feature: FEATURE, page: PAGE_PATH })
}

function formatResultText(data) {
  const p = data.personality || {}
  const lines = [
    '【你的兴趣人格类型】',
    p.type_title || '',
    p.analysis || '',
    '',
    '【为什么以前容易坚持不下去】',
    p.why_past_failed || '',
    '',
    '【最适合你的兴趣推荐】',
  ]

  ;(data.interests || []).forEach((item, idx) => {
    lines.push(`\n${idx + 1}. ${item.name}`)
    if (item.why_fit) lines.push(`为什么适合你：${item.why_fit}`)
    lines.push(`入门难度：${item.difficulty}/5`)
    lines.push(`花费：${item.cost_level} | 社交：${item.social_level}`)
    if (item.long_term) lines.push(`长期坚持：${item.long_term}`)
    if (item.best_time) lines.push(`适合开始：${item.best_time}`)
    if (item.starter_tip) lines.push(`新手入门：${item.starter_tip}`)
  })

  if (data.avoid?.length) {
    lines.push('', '【不建议你尝试的兴趣】')
    data.avoid.forEach((x) => lines.push(`- ${x}`))
  }

  if (data.week_plan?.length) {
    lines.push('', '【一周兴趣体验建议】')
    data.week_plan.forEach((w) => lines.push(`${w.day}：${w.activity}`))
  }

  if (data.lazy_fallback) {
    lines.push('', '【如果你完全不想动】')
    if (data.lazy_fallback.title) lines.push(data.lazy_fallback.title)
    lines.push(data.lazy_fallback.description || '')
  }

  return lines.join('\n')
}

async function copyResult() {
  if (!result.value) return
  try {
    await navigator.clipboard.writeText(formatResultText(result.value))
    trackEvent('interest_explorer_copy', { feature: FEATURE, page: PAGE_PATH })
    showToast('已复制兴趣推荐')
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
      <p class="hero-emoji" aria-hidden="true">🌿</p>
      <h1 class="title">不知道培养什么兴趣爱好？</h1>
      <p class="sub">
        也许不是你没兴趣，<br />
        而是你一直在尝试不适合自己的东西。
      </p>
    </header>

    <template v-if="phase === 'form'">
      <InterestExplorerForm v-model="form" :loading="loading" @submit="generateResult" />
    </template>

    <template v-else-if="result">
      <div class="result-wrap" :class="{ 'result-wrap--loading': loading }">
        <p v-if="loading" class="loading-hint" role="status">AI 正在分析适合你的生活节奏...</p>
        <InterestExplorerResult
          v-show="!loading"
          :result="result"
          @regenerate="generateResult"
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
  color: #059669;
  text-decoration: none;
}

.hero {
  margin-bottom: 16px;
  text-align: center;
  background: linear-gradient(160deg, rgba(236, 253, 245, 0.95), rgba(255, 255, 255, 0.98));
  border-color: rgba(16, 185, 129, 0.2);
}

.hero-emoji {
  margin: 0 0 8px;
  font-size: 28px;
}

.card {
  background: var(--surface-solid);
  border-radius: var(--radius);
  padding: 18px 16px;
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
}

.title {
  margin: 0 0 10px;
  font-size: 21px;
  font-weight: 800;
  color: var(--text);
  line-height: 1.35;
}

.sub {
  margin: 0;
  font-size: 14px;
  line-height: 1.7;
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
  color: #059669;
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
