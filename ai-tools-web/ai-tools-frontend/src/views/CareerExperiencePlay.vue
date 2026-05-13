<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import {
  applyStatEffects,
  getCareerExperienceConfig,
  resolveExperienceEnding,
} from '../data/careerExperience/index.js'
import { trackEvent } from '../analytics.js'

const route = useRoute()
const router = useRouter()

const careerId = computed(() => String(route.params.careerId || ''))
const config = computed(() => getCareerExperienceConfig(careerId.value))

/** @type {import('vue').Ref<'intro' | 'playing' | 'ended'>} */
const phase = ref('intro')

/** @type {import('vue').Ref<Array<{ key: string, role: string, text: string }>>} */
const thread = ref([])

const stats = ref({ stress: 0, reputation: 0, growth: 0, mood: 0 })

/** @type {import('vue').Ref<string | null>} */
const currentSceneId = ref(null)

/** @type {import('vue').Ref<{ id: string, label: string, summary: string } | null>} */
const ending = ref(null)

const chatRoot = ref(/** @type {HTMLElement | null} */ (null))
let keySeq = 0
function nextKey() {
  keySeq += 1
  return `m_${keySeq}`
}

const currentScene = computed(() => {
  const c = config.value
  const sid = currentSceneId.value
  if (!c || !sid) return null
  return c.scenes.find((s) => s.id === sid) ?? null
})

function scrollChatToEnd() {
  nextTick(() => {
    const el = chatRoot.value
    if (!el) return
    el.scrollTop = el.scrollHeight
  })
}

watch(
  () => thread.value.length,
  () => scrollChatToEnd(),
)

function resetRun() {
  const c = config.value
  if (!c) return
  phase.value = 'intro'
  thread.value = []
  ending.value = null
  currentSceneId.value = null
  stats.value = { ...c.initialStats }
}

function pushScene(sceneId) {
  const c = config.value
  if (!c) return
  const scene = c.scenes.find((s) => s.id === sceneId)
  if (!scene) return
  thread.value.push({ key: nextKey(), role: 'time', text: scene.time })
  for (const m of scene.messages) {
    thread.value.push({ key: nextKey(), role: 'system', text: m.text })
  }
  currentSceneId.value = sceneId
  scrollChatToEnd()
}

function startWork() {
  const c = config.value
  if (!c) return
  trackEvent('career_experience_start', {
    feature: 'career_experience',
    page: route.path,
    props: { experience_id: c.id },
  })
  phase.value = 'playing'
  thread.value = []
  ending.value = null
  stats.value = { ...c.initialStats }
  currentSceneId.value = null
  pushScene('scene_1')
}

/**
 * @param {{ text: string, nextSceneId: string, effects: Record<string, number> }} opt
 */
function onChoose(opt) {
  const c = config.value
  if (!c || phase.value !== 'playing' || !currentScene.value) return

  thread.value.push({ key: nextKey(), role: 'user', text: opt.text })
  stats.value = applyStatEffects(stats.value, opt.effects)

  if (opt.nextSceneId === '__end__') {
    phase.value = 'ended'
    currentSceneId.value = null
    ending.value = resolveExperienceEnding(stats.value, c.endings)
    trackEvent('career_experience_complete', {
      feature: 'career_experience',
      page: route.path,
      props: {
        experience_id: c.id,
        ending_id: ending.value?.id ?? '',
      },
    })
    scrollChatToEnd()
    return
  }

  pushScene(opt.nextSceneId)
}

function playAgain() {
  resetRun()
}

onMounted(() => {
  if (!config.value) {
    router.replace('/career-experience')
  }
})

watch(careerId, () => {
  if (!config.value) {
    router.replace('/career-experience')
    return
  }
  resetRun()
})

const statRows = computed(() => {
  const s = stats.value
  return [
    { key: 'stress', label: '压力值', value: s.stress },
    { key: 'reputation', label: '职业评价', value: s.reputation },
    { key: 'growth', label: '成长值', value: s.growth },
    { key: 'mood', label: '情绪值', value: s.mood },
  ]
})
</script>

<template>
  <div v-if="config" class="page">
    <div class="top-bar">
      <RouterLink class="back" to="/career-experience">← 职业体验馆</RouterLink>
    </div>

    <!-- 进行中：顶部状态 -->
    <div v-if="phase === 'playing'" class="stats" aria-label="当前状态">
      <div v-for="row in statRows" :key="row.key" class="stat-pill">
        <span class="stat-l">{{ row.label }}</span>
        <span class="stat-v">{{ row.value }}</span>
      </div>
    </div>

    <!-- 开场 -->
    <section v-if="phase === 'intro'" class="intro card-surface">
      <h1 class="h1">{{ config.title }}</h1>
      <p class="sub">{{ config.subtitle }}</p>
      <button type="button" class="btn-start btn-gradient" @click="startWork">{{ config.startCta }}</button>
    </section>

    <!-- 剧情 -->
    <section v-else-if="phase === 'playing'" class="play">
      <div ref="chatRoot" class="chat" role="log" aria-live="polite">
        <div
          v-for="msg in thread"
          :key="msg.key"
          class="msg-row"
          :class="msg.role === 'user' ? 'msg-row--user' : 'msg-row--sys'"
        >
          <div v-if="msg.role === 'time'" class="bubble bubble--time">{{ msg.text }}</div>
          <div v-else-if="msg.role === 'system'" class="bubble bubble--sys">{{ msg.text }}</div>
          <div v-else class="bubble bubble--user">{{ msg.text }}</div>
        </div>
      </div>

      <div v-if="currentScene" class="opts">
        <button
          v-for="(opt, idx) in currentScene.options"
          :key="idx"
          type="button"
          class="opt-btn"
          @click="onChoose(opt)"
        >
          {{ opt.text }}
        </button>
      </div>
    </section>

    <!-- 结局 -->
    <section v-else class="ending card-surface">
      <h1 class="h1">{{ config.endingHeadline }}</h1>
      <p class="end-type">{{ ending?.label }}</p>

      <div class="stats stats--block" aria-label="最终数值">
        <div class="stat-pill"><span class="stat-l">压力值</span><span class="stat-v">{{ stats.stress }}</span></div>
        <div class="stat-pill">
          <span class="stat-l">职业评价</span><span class="stat-v">{{ stats.reputation }}</span>
        </div>
        <div class="stat-pill"><span class="stat-l">成长值</span><span class="stat-v">{{ stats.growth }}</span></div>
        <div class="stat-pill"><span class="stat-l">情绪值</span><span class="stat-v">{{ stats.mood }}</span></div>
      </div>

      <p class="summary">{{ ending?.summary }}</p>

      <div class="end-actions">
        <button type="button" class="btn-secondary" @click="playAgain">再体验一次</button>
        <RouterLink class="btn-outline" to="/career-experience">返回职业体验馆</RouterLink>
      </div>
    </section>
  </div>
</template>

<style scoped>
.page {
  max-width: 720px;
  margin: 0 auto;
  padding: 20px 16px 40px;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.top-bar {
  margin-bottom: 12px;
}

.back {
  font-size: 14px;
  color: var(--text-muted);
  text-decoration: none;
}

.back:hover {
  color: var(--accent-a);
}

.stats {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 0 0 14px;
}

.stats--block {
  margin: 16px 0;
}

.stat-pill {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 10px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.06);
  border: 1px solid rgba(148, 163, 184, 0.35);
  font-size: 12px;
}

.stat-l {
  color: var(--text-muted);
  font-weight: 600;
}

.stat-v {
  font-weight: 800;
  color: var(--text);
  font-variant-numeric: tabular-nums;
}

.intro {
  padding: 28px 22px 32px;
}

.card-surface {
  border-radius: var(--radius);
  background: var(--surface-solid);
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
}

.h1 {
  margin: 0;
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.02em;
}

.sub {
  margin: 14px 0 0;
  font-size: 15px;
  color: var(--text-muted);
  line-height: 1.6;
}

.btn-start {
  margin-top: 24px;
  width: 100%;
  padding: 14px 20px;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 700;
}

.play {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
}

.chat {
  flex: 1;
  min-height: 220px;
  max-height: min(52vh, 420px);
  overflow-y: auto;
  padding: 12px 10px 16px;
  border-radius: var(--radius);
  background: rgba(255, 255, 255, 0.55);
  border: var(--border-soft);
  margin-bottom: 12px;
}

.msg-row {
  display: flex;
  margin-bottom: 10px;
}

.msg-row--sys {
  justify-content: flex-start;
}

.msg-row--user {
  justify-content: flex-end;
}

.bubble {
  max-width: 92%;
  padding: 10px 14px;
  border-radius: 14px;
  font-size: 14px;
  line-height: 1.55;
  white-space: pre-wrap;
}

.bubble--sys {
  background: #f1f5f9;
  border: 1px solid rgba(148, 163, 184, 0.35);
  color: var(--text);
  border-bottom-left-radius: 4px;
}

.bubble--user {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.18), rgba(168, 85, 247, 0.14));
  border: 1px solid rgba(99, 102, 241, 0.28);
  color: #1e1b4b;
  border-bottom-right-radius: 4px;
}

.bubble--time {
  margin: 8px auto 4px;
  max-width: 100%;
  text-align: center;
  font-size: 12px;
  font-weight: 700;
  color: var(--text-muted);
  background: transparent;
  border: none;
  padding: 4px 8px;
}

.opts {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.opt-btn {
  width: 100%;
  text-align: left;
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid rgba(99, 102, 241, 0.35);
  background: var(--surface-solid);
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
  transition:
    background var(--transition),
    border-color var(--transition),
    transform var(--transition);
}

.opt-btn:hover {
  border-color: var(--accent-a);
  background: rgba(99, 102, 241, 0.06);
  transform: translateY(-1px);
}

.ending {
  padding: 26px 22px 28px;
}

.end-type {
  margin: 12px 0 0;
  font-size: 18px;
  font-weight: 800;
  color: #5b21b6;
}

.summary {
  margin: 0;
  font-size: 14px;
  line-height: 1.65;
  color: var(--text-muted);
}

.end-actions {
  margin-top: 22px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn-secondary {
  padding: 13px 18px;
  border-radius: 14px;
  border: var(--border-soft);
  background: #f8fafc;
  font-weight: 700;
  font-size: 15px;
  color: var(--text);
}

.btn-secondary:hover {
  background: #f1f5f9;
}

.btn-outline {
  display: block;
  text-align: center;
  padding: 13px 18px;
  border-radius: 14px;
  border: 1px solid rgba(99, 102, 241, 0.45);
  font-weight: 700;
  font-size: 15px;
  color: #4338ca;
  text-decoration: none;
  background: #fff;
}

.btn-outline:hover {
  background: rgba(99, 102, 241, 0.06);
}
</style>
