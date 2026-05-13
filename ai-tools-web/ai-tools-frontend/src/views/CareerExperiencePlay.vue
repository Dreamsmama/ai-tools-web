<script setup>
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter, RouterLink } from 'vue-router'
import html2canvas from 'html2canvas'
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

/** @type {import('vue').Ref<Array<{ key: string, role: string, text: string, source?: string }>>} */
const thread = ref([])

const stats = ref({ stress: 0, reputation: 0, growth: 0, mood: 0 })

/** @type {import('vue').Ref<string | null>} */
const currentSceneId = ref(null)

/** @type {import('vue').Ref<{ id: string, label: string, punchline?: string, summary: string, fitReason?: string, riskReason?: string, visual?: { symbol: string, name: string, description: string, tags?: string[] } } | null>} */
const ending = ref(null)

const chatRoot = ref(/** @type {HTMLElement | null} */ (null))
const shareCardRoot = ref(/** @type {HTMLElement | null} */ (null))
const isSavingShare = ref(false)
const shareSaveMessage = ref('')
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
  shareSaveMessage.value = ''
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
    thread.value.push({ key: nextKey(), role: 'system', source: m.source, text: m.text })
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
  shareSaveMessage.value = ''
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

async function saveShareCard() {
  const el = shareCardRoot.value
  if (!el || isSavingShare.value) return

  const startedAt = performance.now()
  const eventProps = {
    experience_id: config.value?.id ?? '',
    ending_id: ending.value?.id ?? '',
    ending_label: ending.value?.label ?? '',
  }

  trackEvent('career_experience_share_save_click', {
    feature: 'career_experience',
    page: route.path,
    props: eventProps,
  })

  isSavingShare.value = true
  shareSaveMessage.value = ''
  try {
    const canvas = await html2canvas(el, {
      backgroundColor: null,
      scale: Math.min(window.devicePixelRatio || 2, 3),
      useCORS: true,
    })
    const filename = `打工人格-${ending.value?.label || '结果'}.png`
    const link = document.createElement('a')
    link.download = filename
    link.href = canvas.toDataURL('image/png')
    link.click()
    shareSaveMessage.value = '已生成图片，可以发给朋友了。'
    trackEvent('career_experience_share_save_success', {
      feature: 'career_experience',
      page: route.path,
      duration_ms: performance.now() - startedAt,
      props: eventProps,
    })
  } catch (err) {
    console.error(err)
    shareSaveMessage.value = '保存失败了，可以先截图分享。'
    trackEvent('career_experience_share_save_fail', {
      feature: 'career_experience',
      page: route.path,
      status: 'fail',
      error_code: err?.name || 'share_save_failed',
      duration_ms: performance.now() - startedAt,
      props: eventProps,
    })
  } finally {
    isSavingShare.value = false
  }
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

function describeEndingStat(key, value) {
  if (key === 'stress') {
    if (value <= 20) {
      return {
        state: '节奏稳定',
        note: '今天事情不少，但还没把你整个人按进工位里。',
      }
    }
    if (value <= 50) {
      return {
        state: '压力累积',
        note: '你还撑得住，只是已经开始把“等会再休息”说得很顺口。',
      }
    }
    if (value <= 80) {
      return {
        state: '明显紧绷',
        note: '工作推进很快，但你的恢复空间正在被会议和消息慢慢挤没。',
      }
    }
    return {
      state: '长期高压',
      note: '你已经开始默认：所有问题都应该自己扛。别人一句辛苦了，你就继续把活接下来。',
    }
  }

  if (key === 'mood') {
    if (value >= 80) {
      return {
        state: '状态轻松',
        note: '你今天还能笑出来，而且不是那种“已读不回式微笑”。',
      }
    }
    if (value >= 50) {
      return {
        state: '开始疲惫',
        note: '你还能正常回消息，但心里已经在默默申请下班。',
      }
    }
    if (value >= 20) {
      return {
        state: '情绪压抑',
        note: '你还能继续做事，但很多反应已经不是热情，是职业惯性。',
      }
    }
    return {
      state: '明显透支',
      note: '你已经不是在“坚持”，而是在靠惯性工作。情绪空间几乎被工作占满。',
    }
  }

  if (key === 'reputation') {
    if (value <= 20) {
      return {
        state: '边缘状态',
        note: '今天大家暂时没太指望你，坏消息是你也没太刷到存在感。',
      }
    }
    if (value <= 50) {
      return {
        state: '普通协作',
        note: '你完成了该做的事，没有特别出圈，也没有被重点点名。',
      }
    }
    if (value <= 80) {
      return {
        state: '被持续依赖',
        note: '大家开始默认：有问题先找你。听起来像认可，也像新一轮待办。',
      }
    }
    return {
      state: '核心背锅位',
      note: '你越来越像团队里的稳定处理器：别人更依赖你，也更容易把责任压到你身上。',
    }
  }

  if (value <= 20) {
    return {
      state: '刚进入状态',
      note: '今天更多是在认识混乱本人，成长还没来得及打招呼。',
    }
  }
  if (value <= 50) {
    return {
      state: '开始成长',
      note: '你开始更懂：职场里推进事情，不只是把事情做完。',
    }
  }
  if (value <= 80) {
    return {
      state: '成熟推进者',
      note: '你越来越习惯在压力里做决定，也知道什么时候该留一句说明。',
    }
  }
  return {
    state: '老油条预备役',
    note: '你已经能在混乱里找路，顺便判断这口锅大概会从哪个群飞来。',
  }
}

const endingStatCards = computed(() => {
  const s = stats.value
  return [
    { key: 'stress', label: '压力值', value: s.stress },
    { key: 'mood', label: '情绪值', value: s.mood },
    { key: 'reputation', label: '职业评价', value: s.reputation },
    { key: 'growth', label: '成长值', value: s.growth },
  ].map((row) => ({ ...row, ...describeEndingStat(row.key, row.value) }))
})

const personaVisual = computed(() => {
  return (
    ending.value?.visual ?? {
      symbol: '工',
      name: '普通打工人',
      description: '今天也在工位和消息之间反复横跳。',
      tags: ['稳定上班', '稳定叹气'],
    }
  )
})

const atmosphereClass = computed(() => {
  const s = stats.value
  if (s.stress >= 72 || s.mood <= 36) return 'page--heavy'
  if (s.stress >= 58 || s.mood <= 46) return 'page--tense'
  return ''
})
</script>

<template>
  <div v-if="config" class="page" :class="atmosphereClass">
    <div class="top-bar">
      <RouterLink class="back" to="/career-experience">← 职业体验馆</RouterLink>
    </div>

    <!-- 进行中：顶部状态 -->
    <div v-if="phase === 'playing'" class="stats" aria-label="当前状态">
      <div
        v-for="row in statRows"
        :key="row.key"
        class="stat-pill"
        :class="{
          'stat-pill--pressure': row.key === 'stress' && row.value >= 68,
          'stat-pill--low-mood': row.key === 'mood' && row.value <= 42,
        }"
      >
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
          <div v-else-if="msg.role === 'system'" class="bubble bubble--sys">
            <span v-if="msg.source" class="bubble-source">【{{ msg.source }}】</span>
            <span>{{ msg.text }}</span>
          </div>
          <div v-else class="bubble bubble--user">
            <span class="bubble-source bubble-source--user">【你的选择】</span>
            <span>{{ msg.text }}</span>
          </div>
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
      <p class="end-label">{{ config.endingHeadline }}</p>
      <h1 class="h1 ending-title">打工人格</h1>

      <div class="persona-hero">
        <div class="persona-visual" aria-hidden="true">
          <span class="persona-symbol">{{ personaVisual.symbol }}</span>
          <span class="persona-shadow" />
        </div>
        <div class="persona-copy">
          <p class="end-kicker">你的结果是</p>
          <p class="end-type">{{ ending?.label }}</p>
          <p class="persona-name">{{ personaVisual.name }}</p>
        </div>
      </div>

      <p v-if="ending?.punchline" class="end-punchline">“{{ ending.punchline }}”</p>
      <p class="persona-desc">{{ personaVisual.description }}</p>
      <div v-if="personaVisual.tags?.length" class="persona-tags" aria-label="人格小形象特征">
        <span v-for="tag in personaVisual.tags" :key="tag" class="persona-tag">{{ tag }}</span>
      </div>

      <p class="summary">{{ ending?.summary }}</p>

      <section ref="shareCardRoot" class="share-card" aria-label="打工人格分享卡片">
        <div class="share-card-top">
          <span class="share-brand">AI 职业体验馆</span>
          <span class="share-sub">体验一次真实职业的一天</span>
        </div>

        <div class="share-persona">
          <div class="share-visual" aria-hidden="true">{{ personaVisual.symbol }}</div>
          <div class="share-persona-copy">
            <p class="share-persona-label">我的打工人格</p>
            <h2 class="share-persona-title">{{ ending?.label }}</h2>
            <p class="share-persona-name">{{ personaVisual.name }}</p>
          </div>
        </div>

        <p v-if="ending?.punchline" class="share-punchline">“{{ ending.punchline }}”</p>

        <div class="share-status-list" aria-label="状态标签">
          <span v-for="card in endingStatCards" :key="card.key" class="share-status-tag">
            <span>{{ card.state }}</span>
            <small>{{ card.value }}</small>
          </span>
        </div>

        <div class="share-card-bottom">
          <div class="share-bottom-copy">
            <p class="share-cta">来测测你是哪种打工人格</p>
            <p class="share-url">47.116.6.242/career-experience</p>
          </div>
          <span class="share-entry-btn">进入体验馆</span>
        </div>
      </section>

      <div class="share-actions">
        <button type="button" class="share-save-btn" :disabled="isSavingShare" @click="saveShareCard">
          <span>{{ isSavingShare ? '生成中...' : '保存我的打工人格' }}</span>
          <small>{{ isSavingShare ? '正在生成分享海报' : '生成分享海报' }}</small>
        </button>
        <p v-if="shareSaveMessage" class="share-save-message">{{ shareSaveMessage }}</p>
      </div>

      <div class="ending-stats" aria-label="最终状态解释">
        <article v-for="card in endingStatCards" :key="card.key" class="ending-stat-card">
          <div class="ending-stat-head">
            <span class="ending-stat-label">{{ card.label }}</span>
            <span class="ending-stat-value">{{ card.value }}</span>
          </div>
          <p class="ending-stat-state">状态：{{ card.state }}</p>
          <p class="ending-stat-note">{{ card.note }}</p>
        </article>
      </div>

      <div v-if="ending?.fitReason || ending?.riskReason" class="end-reflection">
        <div v-if="ending?.fitReason" class="reflection-card">
          <span class="reflection-title">还算扛住的地方</span>
          <p>{{ ending.fitReason }}</p>
        </div>
        <div v-if="ending?.riskReason" class="reflection-card reflection-card--risk">
          <span class="reflection-title">扎心提示</span>
          <p>{{ ending.riskReason }}</p>
        </div>
      </div>

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
  transition:
    background 180ms ease,
    filter 180ms ease;
}

.page--tense {
  background: linear-gradient(180deg, rgba(241, 245, 249, 0.28), rgba(226, 232, 240, 0.18));
}

.page--heavy {
  background: linear-gradient(180deg, rgba(226, 232, 240, 0.5), rgba(203, 213, 225, 0.28));
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

.stats--soft {
  opacity: 0.82;
}

.share-card {
  margin: 18px auto 0;
  width: min(100%, 380px);
  padding: 18px 18px 16px;
  border-radius: 26px;
  background:
    radial-gradient(circle at 16% 14%, rgba(255, 255, 255, 0.95), transparent 26%),
    linear-gradient(160deg, #eef2ff 0%, #fdf4ff 52%, #f8fafc 100%);
  border: 1px solid rgba(99, 102, 241, 0.22);
  box-shadow: 0 20px 42px rgba(79, 70, 229, 0.18);
  color: #1e1b4b;
}

.share-card-top {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  align-items: center;
}

.share-brand {
  font-size: 14px;
  font-weight: 900;
}

.share-sub {
  font-size: 11px;
  font-weight: 800;
  color: #64748b;
  text-align: right;
}

.share-persona {
  margin-top: 16px;
  display: grid;
  grid-template-columns: 96px minmax(0, 1fr);
  gap: 14px;
  align-items: center;
}

.share-visual {
  width: 96px;
  height: 96px;
  border-radius: 30px;
  display: grid;
  place-items: center;
  background:
    radial-gradient(circle at 34% 24%, rgba(255, 255, 255, 0.95), transparent 30%),
    linear-gradient(135deg, rgba(99, 102, 241, 0.34), rgba(168, 85, 247, 0.26));
  border: 1px solid rgba(99, 102, 241, 0.22);
  box-shadow: 0 14px 28px rgba(79, 70, 229, 0.18);
  font-size: 34px;
  font-weight: 900;
  color: #4c1d95;
}

.share-persona-label {
  margin: 0;
  font-size: 11px;
  font-weight: 900;
  letter-spacing: 0.1em;
  color: #64748b;
}

.share-persona-title {
  margin: 6px 0 0;
  font-size: 25px;
  line-height: 1.12;
  letter-spacing: -0.03em;
  color: #312e81;
}

.share-persona-name {
  margin: 8px 0 0;
  font-size: 13px;
  font-weight: 900;
  color: #475569;
}

.share-punchline {
  margin: 16px 0 0;
  padding: 14px;
  border-radius: 18px;
  background: rgba(255, 255, 255, 0.76);
  border: 1px solid rgba(99, 102, 241, 0.16);
  font-size: 18px;
  line-height: 1.55;
  font-weight: 900;
  color: #312e81;
}

.share-status-list {
  margin-top: 12px;
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.share-status-tag {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 7px 9px;
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.68);
  border: 1px solid rgba(148, 163, 184, 0.26);
  font-size: 12px;
  font-weight: 900;
  color: #334155;
}

.share-status-tag small {
  font-size: 10px;
  color: #94a3b8;
  font-variant-numeric: tabular-nums;
}

.share-card-bottom {
  margin-top: 16px;
  padding: 14px;
  border-radius: 20px;
  background: rgba(255, 255, 255, 0.72);
  border-top: 1px dashed rgba(99, 102, 241, 0.24);
  display: flex;
  justify-content: space-between;
  gap: 14px;
  align-items: center;
}

.share-bottom-copy {
  min-width: 0;
}

.share-cta {
  margin: 0;
  font-size: 14px;
  font-weight: 900;
}

.share-url {
  margin: 6px 0 0;
  font-size: 13px;
  line-height: 1.2;
  font-weight: 900;
  color: #4f46e5;
  word-break: break-all;
}

.share-entry-btn {
  display: inline-flex;
  flex: 0 0 auto;
  padding: 9px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 900;
  color: #fff;
  background: linear-gradient(135deg, #4f46e5, #9333ea);
  box-shadow: 0 10px 18px rgba(79, 70, 229, 0.18);
}

.share-actions {
  margin-top: 16px;
  display: grid;
  gap: 6px;
}

.share-save-btn {
  width: 100%;
  padding: 13px 16px 12px;
  border: none;
  border-radius: 16px;
  color: white;
  background: linear-gradient(135deg, #4f46e5, #9333ea);
  box-shadow: 0 12px 24px rgba(79, 70, 229, 0.22);
}

.share-save-btn span,
.share-save-btn small {
  display: block;
}

.share-save-btn span {
  font-size: 15px;
  font-weight: 900;
}

.share-save-btn small {
  margin-top: 3px;
  font-size: 11px;
  font-weight: 800;
  opacity: 0.78;
}

.share-save-btn:disabled {
  opacity: 0.7;
}

.share-save-message {
  margin: 0;
  text-align: center;
  font-size: 12px;
  font-weight: 800;
  color: #64748b;
}

.ending-stats {
  margin: 18px 0 18px;
  display: grid;
  gap: 10px;
}

.ending-stat-card {
  padding: 13px 14px;
  border-radius: 16px;
  background: rgba(248, 250, 252, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.28);
}

.ending-stat-head {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  gap: 12px;
}

.ending-stat-label {
  font-size: 13px;
  font-weight: 800;
  color: var(--text);
}

.ending-stat-value {
  font-size: 16px;
  font-weight: 900;
  color: #475569;
  font-variant-numeric: tabular-nums;
}

.ending-stat-state {
  margin: 7px 0 0;
  font-size: 14px;
  font-weight: 800;
  color: #5b21b6;
}

.ending-stat-note {
  margin: 6px 0 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-muted);
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

.stat-pill--pressure {
  background: rgba(71, 85, 105, 0.12);
  border-color: rgba(71, 85, 105, 0.36);
}

.stat-pill--low-mood {
  background: rgba(30, 41, 59, 0.1);
  border-color: rgba(51, 65, 85, 0.32);
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
  transition:
    background 180ms ease,
    border-color 180ms ease,
    box-shadow 180ms ease;
}

.page--tense .chat {
  background: rgba(248, 250, 252, 0.72);
  border-color: rgba(100, 116, 139, 0.42);
}

.page--heavy .chat {
  background: linear-gradient(180deg, rgba(241, 245, 249, 0.92), rgba(226, 232, 240, 0.82));
  border-color: rgba(71, 85, 105, 0.44);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.5);
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

.bubble-source {
  display: block;
  margin-bottom: 4px;
  font-size: 11px;
  font-weight: 800;
  line-height: 1.2;
  color: #64748b;
}

.bubble-source--user {
  color: #4338ca;
}

.bubble--sys {
  background: #f1f5f9;
  border: 1px solid rgba(148, 163, 184, 0.35);
  color: var(--text);
  border-bottom-left-radius: 4px;
}

.page--heavy .bubble--sys {
  background: #e8edf4;
  border-color: rgba(100, 116, 139, 0.42);
}

.bubble--user {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.18), rgba(168, 85, 247, 0.14));
  border: 1px solid rgba(99, 102, 241, 0.28);
  color: #1e1b4b;
  border-bottom-right-radius: 4px;
}

.page--heavy .bubble--user {
  background: linear-gradient(135deg, rgba(79, 70, 229, 0.16), rgba(100, 116, 139, 0.16));
  border-color: rgba(79, 70, 229, 0.22);
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

.page--heavy .opt-btn {
  border-color: rgba(100, 116, 139, 0.36);
  background: rgba(255, 255, 255, 0.82);
}

.ending {
  padding: 26px 22px 28px;
  position: relative;
  overflow: hidden;
}

.ending::before {
  content: '';
  position: absolute;
  inset: 0 0 auto;
  height: 214px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(168, 85, 247, 0.1));
  pointer-events: none;
}

.ending > * {
  position: relative;
}

.end-label {
  margin: 0;
  font-size: 12px;
  font-weight: 800;
  color: var(--text-muted);
}

.ending-title {
  margin-top: 8px;
  font-size: 30px;
}

.persona-hero {
  margin-top: 16px;
  display: grid;
  grid-template-columns: 96px minmax(0, 1fr);
  gap: 16px;
  align-items: center;
}

.persona-visual {
  position: relative;
  width: 96px;
  height: 96px;
  border-radius: 28px;
  display: grid;
  place-items: center;
  background:
    radial-gradient(circle at 30% 20%, rgba(255, 255, 255, 0.86), transparent 34%),
    linear-gradient(135deg, rgba(99, 102, 241, 0.26), rgba(168, 85, 247, 0.2));
  border: 1px solid rgba(99, 102, 241, 0.22);
  box-shadow: 0 18px 36px rgba(79, 70, 229, 0.16);
}

.persona-symbol {
  position: relative;
  z-index: 1;
  width: 58px;
  height: 58px;
  border-radius: 999px;
  display: grid;
  place-items: center;
  background: rgba(255, 255, 255, 0.84);
  border: 1px solid rgba(99, 102, 241, 0.18);
  color: #4c1d95;
  font-size: 28px;
  font-weight: 900;
  box-shadow: 0 8px 18px rgba(15, 23, 42, 0.1);
}

.persona-shadow {
  position: absolute;
  bottom: 14px;
  width: 48px;
  height: 10px;
  border-radius: 999px;
  background: rgba(79, 70, 229, 0.18);
  filter: blur(1px);
}

.persona-copy {
  min-width: 0;
}

.end-type {
  margin: 8px 0 0;
  font-size: 25px;
  line-height: 1.18;
  font-weight: 800;
  color: #5b21b6;
}

.end-kicker {
  margin: 18px 0 0;
  font-size: 12px;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: var(--text-muted);
}

.persona-hero .end-kicker {
  margin-top: 0;
}

.persona-name {
  margin: 8px 0 0;
  font-size: 13px;
  font-weight: 800;
  color: #475569;
}

.end-punchline {
  margin: 14px 0 0;
  padding: 13px 14px;
  border-radius: 16px;
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(99, 102, 241, 0.18);
  font-size: 15px;
  line-height: 1.65;
  font-weight: 800;
  color: #312e81;
}

.persona-desc {
  margin: 12px 0 0;
  font-size: 13px;
  line-height: 1.65;
  color: var(--text-muted);
}

.persona-tags {
  margin-top: 10px;
  display: flex;
  flex-wrap: wrap;
  gap: 7px;
}

.persona-tag {
  padding: 5px 9px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 800;
  color: #4338ca;
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.16);
}

.summary {
  margin: 16px 0 0;
  font-size: 15px;
  line-height: 1.75;
  color: var(--text);
}

.end-reflection {
  margin-top: 16px;
  display: grid;
  gap: 10px;
}

.reflection-card {
  padding: 13px 14px;
  border-radius: 14px;
  background: rgba(99, 102, 241, 0.06);
  border: 1px solid rgba(99, 102, 241, 0.16);
}

.reflection-card--risk {
  background: rgba(71, 85, 105, 0.06);
  border-color: rgba(100, 116, 139, 0.2);
}

.reflection-title {
  display: block;
  margin-bottom: 6px;
  font-size: 13px;
  font-weight: 800;
  color: #334155;
}

.reflection-card p {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-muted);
}

.share-hint {
  margin: 16px 0 0;
  padding: 11px 12px;
  border-radius: 999px;
  text-align: center;
  font-size: 13px;
  font-weight: 800;
  color: #4338ca;
  background: rgba(99, 102, 241, 0.08);
  border: 1px dashed rgba(99, 102, 241, 0.32);
}

@media (max-width: 420px) {
  .persona-hero {
    grid-template-columns: 82px minmax(0, 1fr);
    gap: 12px;
  }

  .persona-visual {
    width: 82px;
    height: 82px;
    border-radius: 24px;
  }

  .persona-symbol {
    width: 50px;
    height: 50px;
    font-size: 24px;
  }

  .end-type {
    font-size: 22px;
  }
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
