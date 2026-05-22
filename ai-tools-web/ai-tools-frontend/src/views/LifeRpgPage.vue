<script setup>
import { computed, onMounted, ref } from 'vue'
import { RouterLink } from 'vue-router'
import LifeRpgCreateForm from '../components/lifeRpg/LifeRpgCreateForm.vue'
import LifeRpgHome from '../components/lifeRpg/LifeRpgHome.vue'
import LifeRpgResult from '../components/lifeRpg/LifeRpgResult.vue'
import LifeRpgRouteReady from '../components/lifeRpg/LifeRpgRouteReady.vue'
import ErrorDialog from '../components/ErrorDialog.vue'
import {
  DAILY_MODE_OPTIONS,
  ENERGY_OPTIONS,
  GO_OUT_OPTIONS,
  buildProfileFromRoute,
  characterFormFromProfile,
  createDefaultCharacterForm,
  validateCharacterForm,
} from '../data/lifeRpgOptions.js'
import { requestLifeRpgCreateRoute, requestLifeRpgDaily } from '../lib/lifeRpgApi.js'
import { findTaskById, normalizeLifeRpgResult } from '../lib/lifeRpgNormalize.js'
import {
  applyReward,
  hasLifeRpgProfile,
  loadAttributes,
  loadCompletedTasks,
  loadDailyForm,
  loadLastResult,
  loadProfile,
  purgeLegacyLifeRpgStorage,
  resetLifeRpgAll,
  saveCompletedTasks,
  saveDailyForm,
  saveLastResult,
  saveLifeRpgProfile,
  subtractReward,
} from '../lib/lifeRpgStorage.js'
import { trackApiFail, trackApiSuccess, trackEvent, trackSubmit } from '../analytics.js'

const PAGE_PATH = '/tools/life-rpg'
const FEATURE = 'life_rpg'

/** @typedef {'create-character'|'generating-route'|'route-ready'|'today-world'|'edit-character'|'result'} LifeRpgPhase */

function createDefaultDailyForm() {
  const last = loadDailyForm()
  return {
    energy_level: last?.energy_level || ENERGY_OPTIONS[1],
    daily_mode: last?.daily_mode || DAILY_MODE_OPTIONS[0],
    go_out: last?.go_out || GO_OUT_OPTIONS[0],
    custom_tasks: last?.custom_tasks || '',
  }
}

function newResultId() {
  return `rpg_${Date.now()}`
}

const phase = ref(/** @type {LifeRpgPhase} */ ('create-character'))
const profile = ref(loadProfile())
const createForm = ref(createDefaultCharacterForm())
const dailyForm = ref(createDefaultDailyForm())
const loading = ref(false)
const result = ref(null)
const attributes = ref(loadAttributes())
const completedTaskIds = ref([])
const rawFallback = ref('')
const toast = ref('')
const errorDialog = ref(false)
const errorText = ref('')

const heroMeta = computed(() => {
  const map = {
    'create-character': {
      kicker: '第一步 · 创建人生角色',
      title: 'AI 人生副本',
      sub: '说说你最近的状态与方向，AI 会帮你整理一条长期路线。',
    },
    'edit-character': {
      kicker: '调整人生角色',
      title: 'AI 人生副本',
      sub: '更新状态与关键词后，路线会重新生成。',
    },
    'generating-route': {
      kicker: '第二步 · 生成人生路线',
      title: '正在生成路线',
      sub: '根据你的人生状态与关键词，整理长期路线…',
    },
    'route-ready': {
      kicker: '路线已就绪',
      title: 'AI 人生副本',
      sub: '角色与路线已生成，可以开始今天。',
    },
    'today-world': {
      kicker: '第三步 · 今天',
      title: 'AI 人生副本',
      sub: '轻量同步今天的状态，生成今日安排。',
    },
    result: {
      kicker: '今日安排',
      title: 'AI 人生副本',
      sub: '按你的节奏推进即可，不必一次做完。',
    },
  }
  return map[phase.value] || map['create-character']
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

function initPhase() {
  if (hasLifeRpgProfile()) {
    profile.value = loadProfile()
    phase.value = 'today-world'
  } else {
    phase.value = 'create-character'
  }
}

function looksLikeJsonArtifact(text) {
  const t = (text || '').trim()
  if (!t) return false
  if (t === '原始输出模式' || t.includes('待解析')) return true
  return /^"?\w+"?\s*:\s*/.test(t) && t.length < 160
}

function detectRawFallback(data) {
  if (!data) return ''
  const world = data.world_state || {}
  if (looksLikeJsonArtifact(world.title) || looksLikeJsonArtifact(world.description)) {
    return [world.title, world.description, data.role_summary].filter(Boolean).join('\n')
  }
  const main = data.main_quest || {}
  if (looksLikeJsonArtifact(main.title) || looksLikeJsonArtifact(main.goal)) {
    return [main.title, main.goal].filter(Boolean).join('\n')
  }
  const tasks = main.tasks || []
  if (tasks.some((t) => looksLikeJsonArtifact(t.title) || looksLikeJsonArtifact(t.action))) {
    return '模型返回格式异常，请点击重新生成。'
  }
  return ''
}

function persistResult(data) {
  result.value = data
  saveLastResult(data)
}

async function submitCreateRoute() {
  const v = validateCharacterForm(createForm.value)
  if (!v.ok) {
    showErrorDetail(v.message)
    return
  }

  loading.value = true
  phase.value = 'generating-route'
  const trackEventId = trackSubmit(FEATURE, PAGE_PATH)
  const res = await requestLifeRpgCreateRoute(createForm.value)

  if (!res.ok) {
    trackApiFail(FEATURE, PAGE_PATH, trackEventId, res.kind, 0)
    showErrorDetail(res.message)
    phase.value = hasLifeRpgProfile() ? 'edit-character' : 'create-character'
    loading.value = false
    return
  }

  trackApiSuccess(FEATURE, PAGE_PATH, trackEventId, 0)
  profile.value = buildProfileFromRoute(res.data, createForm.value)
  saveLifeRpgProfile(profile.value)
  loading.value = false
  phase.value = 'route-ready'
  trackEvent('life_rpg_route_created', { feature: FEATURE, page: PAGE_PATH })
}

function onCreateInvalid(message) {
  showErrorDetail(message)
}

async function submitEditCharacter() {
  await submitCreateRoute()
}

function enterTodayWorld() {
  profile.value = loadProfile()
  phase.value = 'today-world'
  dailyForm.value = createDefaultDailyForm()
}

function editCharacter() {
  createForm.value = characterFormFromProfile(profile.value)
  phase.value = 'edit-character'
}

async function generateDaily() {
  const f = dailyForm.value
  if (!(f.energy_level || '').trim()) {
    showErrorDetail('请选择今天的精力状态。')
    return
  }
  if (!(f.daily_mode || '').trim()) {
    showErrorDetail('请选择今天想怎么推进。')
    return
  }
  if (!(f.go_out || '').trim()) {
    showErrorDetail('请选择今天是否想出门。')
    return
  }

  loading.value = true
  const requestStart = Date.now()
  const trackEventId = trackSubmit(FEATURE, PAGE_PATH)
  trackEvent('life_rpg_daily_submit', { feature: FEATURE, page: PAGE_PATH })

  saveDailyForm(f)

  const last = loadLastResult()
  const completed = loadCompletedTasks()

  const res = await requestLifeRpgDaily({
    profile: profile.value || loadProfile(),
    attributes: loadAttributes(),
    last_result: last || undefined,
    completed_task_ids: completed.completedTaskIds || [],
    energy_level: f.energy_level,
    daily_mode: f.daily_mode,
    go_out: f.go_out,
    custom_tasks: (f.custom_tasks || '').trim(),
  })

  if (!res.ok) {
    trackApiFail(FEATURE, PAGE_PATH, trackEventId, res.kind, Date.now() - requestStart)
    showErrorDetail(res.message)
    loading.value = false
    return
  }

  trackApiSuccess(FEATURE, PAGE_PATH, trackEventId, Date.now() - requestStart)

  const normalized = normalizeLifeRpgResult({
    ...res.data,
    result_id: newResultId(),
  })
  rawFallback.value = detectRawFallback(normalized)
  completedTaskIds.value = []
  saveCompletedTasks(normalized.result_id, [])
  persistResult(normalized)

  phase.value = 'result'
  loading.value = false
  trackEvent('life_rpg_result_view', { feature: FEATURE, page: PAGE_PATH })
}

function goTodayWorld() {
  profile.value = loadProfile()
  phase.value = 'today-world'
}

function confirmReset() {
  if (!window.confirm('将清除人生角色、路线与记录，确定重置？')) return
  resetLifeRpgAll()
  profile.value = null
  result.value = null
  attributes.value = loadAttributes()
  completedTaskIds.value = []
  createForm.value = createDefaultCharacterForm()
  dailyForm.value = createDefaultDailyForm()
  phase.value = 'create-character'
  showToast('已重置，请重新创建角色')
  trackEvent('life_rpg_reset', { feature: FEATURE, page: PAGE_PATH })
}

function onToggleTask(taskId) {
  if (!result.value) return
  const task = findTaskById(result.value, taskId)
  if (!task) return

  const ids = [...completedTaskIds.value]
  const idx = ids.indexOf(taskId)
  const rid = result.value.result_id

  if (idx >= 0) {
    ids.splice(idx, 1)
    attributes.value = subtractReward(task.reward)
  } else {
    ids.push(taskId)
    attributes.value = applyReward(task.reward)
  }

  completedTaskIds.value = ids
  saveCompletedTasks(rid, ids)
}

function formatResultText(data) {
  const p = profile.value || loadProfile()
  const lines = [
    '【AI 人生副本】',
    p?.routeTitle ? `人生路线：${p.routeTitle}` : '',
    data.route_continuation || '',
    '',
    '【今日状态】',
    data.world_state?.title || '',
    data.world_state?.description || '',
    '',
    '【主线】',
    data.main_quest?.title || '',
    data.main_quest?.goal || '',
  ]
  ;(data.main_quest?.tasks || []).forEach((t) => {
    const mark = completedTaskIds.value.includes(t.id) ? '✓ ' : ''
    lines.push(`${mark}${t.title}：${t.action}`)
  })

  if (data.side_quests?.length) {
    lines.push('', '【支线】')
    data.side_quests.forEach((sq) => {
      const mark = completedTaskIds.value.includes(sq.id) ? '✓ ' : ''
      lines.push(`${mark}${sq.title}：${sq.action}`)
    })
  }

  if (data.not_recommend?.length) {
    lines.push('', '【今日不建议】')
    data.not_recommend.forEach((x) => lines.push(`· ${x}`))
  }

  if (data.ending) lines.push('', data.ending)
  return lines.filter(Boolean).join('\n')
}

async function copyResult() {
  if (!result.value) return
  try {
    await navigator.clipboard.writeText(formatResultText(result.value))
    showToast('已复制今日安排')
  } catch {
    showToast('复制失败')
  }
}

onMounted(() => {
  purgeLegacyLifeRpgStorage()
  attributes.value = loadAttributes()
  initPhase()
  if (phase.value === 'today-world') {
    profile.value = loadProfile()
    dailyForm.value = createDefaultDailyForm()
  }
})
</script>

<template>
  <div class="life-rpg page">
    <nav class="top-nav">
      <RouterLink class="nav-link" to="/">← 首页</RouterLink>
      <RouterLink class="nav-link nav-link--secondary" to="/tools">工具库</RouterLink>
    </nav>

    <header class="hero tool-card">
      <p class="hero-kicker">{{ heroMeta.kicker }}</p>
      <h1 class="title">{{ heroMeta.title }}</h1>
      <p class="sub">{{ heroMeta.sub }}</p>
    </header>

    <template v-if="phase === 'create-character'">
      <LifeRpgCreateForm
        v-model="createForm"
        :loading="loading"
        @submit="submitCreateRoute"
        @invalid="onCreateInvalid"
      />
    </template>

    <template v-else-if="phase === 'edit-character'">
      <LifeRpgCreateForm
        v-model="createForm"
        :loading="loading"
        edit-mode
        @submit="submitEditCharacter"
        @invalid="onCreateInvalid"
      />
      <button type="button" class="btn-outline back-btn" @click="enterTodayWorld">取消，返回今天</button>
    </template>

    <template v-else-if="phase === 'generating-route'">
      <section class="tool-card tool-card--soft generating-card">
        <p class="loading-hint" role="status">AI 正在根据你的角色塑造人生路线…</p>
        <p class="generating-sub">人生状态、方向模板与关键词已记录，请稍候。</p>
      </section>
    </template>

    <template v-else-if="phase === 'route-ready' && profile">
      <LifeRpgRouteReady
        :profile="profile"
        @enter-today="enterTodayWorld"
        @edit-character="editCharacter"
      />
    </template>

    <template v-else-if="phase === 'today-world' && profile">
      <LifeRpgHome
        :profile="profile"
        :daily-form="dailyForm"
        :loading="loading"
        @update:daily-form="dailyForm = $event"
        @submit-daily="generateDaily"
        @edit-character="editCharacter"
        @reset="confirmReset"
      />
    </template>

    <template v-else-if="phase === 'result' && result">
      <div class="result-wrap" :class="{ 'result-wrap--loading': loading }">
        <p v-if="loading" class="loading-hint" role="status">AI 正在生成你今天的安排…</p>
        <LifeRpgResult
          v-show="!loading"
          :profile="profile"
          :result="result"
          :attributes="attributes"
          :completed-task-ids="completedTaskIds"
          :raw-fallback="rawFallback"
          @regenerate="generateDaily"
          @edit-today="goTodayWorld"
          @back-home="goTodayWorld"
          @copy="copyResult"
          @toggle-task="onToggleTask"
        />
      </div>
    </template>

    <div v-if="toast" class="toast" role="status">{{ toast }}</div>
    <ErrorDialog v-model="errorDialog" :text="errorText" />
  </div>
</template>

<style src="../components/lifeRpg/lifeRpgTheme.css"></style>

<style scoped>
.back-btn {
  margin-top: 8px;
}

.generating-card {
  text-align: center;
  padding: 28px 16px;
}

.generating-sub {
  margin: 0;
  font-size: 13px;
  color: var(--text-muted);
}

.result-wrap--loading {
  min-height: 200px;
}
</style>
