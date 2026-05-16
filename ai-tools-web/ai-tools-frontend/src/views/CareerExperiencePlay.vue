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
import {
  DRAMA_MOMENTS,
  dramaDelay,
  formatSceneChapter,
  inferMessageTone,
  inferTypingName,
} from '../lib/dramaPlayback.js'
import { isSoundMuted, playDramaSound, setSoundMuted, unlockDramaAudio } from '../lib/dramaSounds.js'
import { getSceneVisual } from '../data/careerExperience/sceneVisuals.js'
import SceneCineIcon from '../components/SceneCineIcon.vue'

const route = useRoute()
const router = useRouter()

const isWorkerLab = computed(() => route.path.startsWith('/worker-lab'))
const seriesId = computed(() => String(route.params.seriesId || route.params.careerId || ''))
const episodeId = computed(() => String(route.params.episodeId || ''))
const experienceKey = computed(() => {
  if (isWorkerLab.value) {
    if (episodeId.value) return `${seriesId.value}-${episodeId.value}`
    return seriesId.value
  }
  return String(route.params.careerId || '')
})
const config = computed(() => getCareerExperienceConfig(experienceKey.value))
/** @deprecated 追踪与兼容 */
const careerId = computed(() => experienceKey.value)
const isGaokaoMajor = computed(() => String(experienceKey.value || '').startsWith('major-'))
const hubPath = computed(() => {
  if (isWorkerLab.value) return '/worker-lab'
  if (isGaokaoMajor.value) return '/gaokao'
  return '/career-experience'
})
const hubLabel = computed(() => {
  if (isWorkerLab.value) return '打工人格实验室'
  if (isGaokaoMajor.value) return '高考生专区'
  return '职业体验馆'
})
const shareBrand = computed(() => (isWorkerLab.value ? '打工人格实验室' : 'AI 职业体验馆'))
const shareSub = computed(() =>
  isWorkerLab.value ? '互动职场连续剧 · 一集一个崩溃' : '体验一次真实职业的一天',
)
const shareCta = computed(() =>
  isWorkerLab.value ? '来追一集打工连续剧' : '来体验一次真实职业的一天',
)
const shareUrl = computed(() =>
  isWorkerLab.value ? '47.116.6.242/worker-lab' : '47.116.6.242/career-experience',
)
const startCtaLabel = computed(() => (isWorkerLab.value ? config.value?.startCta : '开始上班') ?? '开始上班')
const endingHeadline = computed(() => {
  const c = config.value
  if (!c) return ''
  if (isWorkerLab.value) return c.endingHeadline
  if (c.id === 'developer') return '你的程序员一天结束了'
  if (c.id === 'hr') return '你的 HR 一天结束了'
  return `你的${c.title}结束了`
})

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
const soundMuted = ref(isSoundMuted())
/** @type {import('vue').Ref<{ name: string } | null>} */
const typingIndicator = ref(null)
const sceneRevealing = ref(false)
const activeAtmosphere = ref('')
const activeSceneBg = ref('')
const sceneBgVisible = ref(false)
/** 消息逐条播放时当前场景（选项出现前 currentSceneId 为空） */
const revealingSceneId = ref(/** @type {string | null} */ (null))
/** @type {import('vue').Ref<string | null>} */
const activeMoment = ref(null)
let revealGeneration = 0
let momentTimer = /** @type {ReturnType<typeof setTimeout> | null} */ (null)
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

function cancelReveal() {
  revealGeneration += 1
  typingIndicator.value = null
  sceneRevealing.value = false
  if (momentTimer) {
    clearTimeout(momentTimer)
    momentTimer = null
  }
  activeMoment.value = null
}

function resetRun() {
  const c = config.value
  if (!c) return
  cancelReveal()
  phase.value = 'intro'
  thread.value = []
  ending.value = null
  shareSaveMessage.value = ''
  currentSceneId.value = null
  revealingSceneId.value = null
  activeAtmosphere.value = ''
  activeSceneBg.value = ''
  sceneBgVisible.value = false
  stats.value = { ...c.initialStats }
}

function applySceneAmbience(scene) {
  if (!scene || !isWorkerLab.value) return
  activeAtmosphere.value = scene.atmosphere || config.value?.defaultAtmosphere || ''
  const nextBg = scene.sceneBg || ''
  sceneBgVisible.value = false
  activeSceneBg.value = nextBg
  if (nextBg) {
    nextTick(() => {
      sceneBgVisible.value = true
    })
  }
}

function toggleSoundMuted() {
  soundMuted.value = !soundMuted.value
  setSoundMuted(soundMuted.value)
}

function pushSceneInstant(sceneId) {
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

async function revealScene(sceneId) {
  const c = config.value
  if (!c) return
  const scene = c.scenes.find((s) => s.id === sceneId)
  if (!scene) return

  if (!isWorkerLab.value) {
    pushSceneInstant(sceneId)
    return
  }

  const gen = ++revealGeneration
  sceneRevealing.value = true
  currentSceneId.value = null
  revealingSceneId.value = sceneId
  typingIndicator.value = null
  applySceneAmbience(scene)

  // 场景标题只在顶部环境条展示，避免聊天区重复
  await dramaDelay(400, 600)
  if (gen !== revealGeneration) return

  for (const m of scene.messages) {
    const tone = m.tone || inferMessageTone(m.source)
    typingIndicator.value = { name: inferTypingName(m.source) }
    await dramaDelay(520, 1100)
    if (gen !== revealGeneration) return

    typingIndicator.value = null

    if (m.moment) {
      activeMoment.value = m.moment
      if (momentTimer) clearTimeout(momentTimer)
      momentTimer = setTimeout(() => {
        if (gen === revealGeneration) activeMoment.value = null
        momentTimer = null
      }, 2000)
    }

    thread.value.push({
      key: nextKey(),
      role: 'system',
      source: m.source,
      text: m.text,
      tone,
      enter: true,
    })
    playDramaSound(tone, soundMuted.value)
    scrollChatToEnd()
    await dramaDelay(820, 1180)
    if (gen !== revealGeneration) return
  }

  typingIndicator.value = null
  sceneRevealing.value = false
  currentSceneId.value = sceneId
  revealingSceneId.value = null
  scrollChatToEnd()
}

function pushScene(sceneId) {
  revealScene(sceneId)
}

function startWork() {
  const c = config.value
  if (!c) return
  if (isWorkerLab.value) unlockDramaAudio()
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
  if (isWorkerLab.value) {
    const first = c.scenes.find((s) => s.id === 'scene_1')
    applySceneAmbience(first)
  } else {
    activeAtmosphere.value = ''
    activeSceneBg.value = ''
  }
  pushScene('scene_1')
}

/**
 * @param {{ text: string, nextSceneId: string, effects: Record<string, number> }} opt
 */
function onChoose(opt) {
  const c = config.value
  if (!c || phase.value !== 'playing' || !currentScene.value || sceneRevealing.value) return

  thread.value.push({ key: nextKey(), role: 'user', text: opt.text })
  scrollChatToEnd()
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
    router.replace(hubPath.value)
  }
})

watch(experienceKey, () => {
  if (!config.value) {
    router.replace(hubPath.value)
    return
  }
  resetRun()
})

const statRows = computed(() => {
  const s = stats.value
  return [
    { key: 'stress', label: '压力值', value: s.stress },
    { key: 'reputation', label: '靠谱度', value: s.reputation },
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
    { key: 'reputation', label: '靠谱度', value: s.reputation },
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
  // 连续剧模式用 page--drama + 场景氛围，不再叠加 page--heavy（否则会冲掉深色气泡文字色）
  if (isWorkerLab.value) return ''
  const s = stats.value
  if (s.stress >= 72 || s.mood <= 36) return 'page--heavy'
  if (s.stress >= 58 || s.mood <= 46) return 'page--tense'
  return ''
})

const activeScene = computed(() => {
  const c = config.value
  const sid = currentSceneId.value || revealingSceneId.value
  if (!c || !sid) return null
  return c.scenes.find((s) => s.id === sid) ?? null
})

const currentSceneChapter = computed(() => {
  if (activeScene.value) return formatSceneChapter(activeScene.value)
  return ''
})

const activeSceneVisual = computed(() => {
  const c = config.value
  const scene = activeScene.value
  if (!c || !scene) return { label: '工位现场', tint: 'default' }
  return getSceneVisual(c.id, scene.id)
})

const showSceneCine = computed(() => isWorkerLab.value && !!activeScene.value)
</script>

<template>
  <div
    v-if="config"
    class="page"
    :class="[atmosphereClass, isWorkerLab && phase === 'playing' ? `page--drama page--${activeAtmosphere}` : '']"
  >
    <div class="top-bar">
      <RouterLink class="back" :to="hubPath">← {{ hubLabel }}</RouterLink>
      <button
        v-if="isWorkerLab && phase === 'playing'"
        type="button"
        class="sound-toggle"
        :aria-pressed="soundMuted"
        :title="soundMuted ? '开启消息提示音' : '关闭消息提示音'"
        @click="toggleSoundMuted"
      >
        {{ soundMuted ? '🔇' : '🔊' }}
      </button>
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
      <p v-if="isWorkerLab && config.episodeCode" class="intro-episode">
        🎬 {{ config.episodeCode }} · {{ config.title }}
      </p>
      <h1 class="h1">{{ config.title }}</h1>
      <p class="sub">{{ config.subtitle }}</p>
      <button type="button" class="btn-start btn-gradient" @click="startWork">{{ startCtaLabel }}</button>
    </section>

    <!-- 剧情 -->
    <section v-else-if="phase === 'playing'" class="play" :class="{ 'play--drama': isWorkerLab }">
      <div
        v-if="showSceneCine"
        class="scene-cine"
        :class="[
          `scene-cine--${activeSceneVisual.tint}`,
          { 'scene-cine--revealing': sceneRevealing },
        ]"
        role="img"
        :aria-label="currentSceneChapter || '当前场景氛围'"
      >
        <div class="scene-cine-art" aria-hidden="true">
          <span class="scene-cine-glow" />
          <SceneCineIcon :name="activeSceneVisual.tint" />
        </div>
        <div class="scene-cine-copy">
          <span class="scene-cine-tag">{{ activeSceneVisual.label }}</span>
          <p v-if="currentSceneChapter" class="scene-cine-title">{{ currentSceneChapter }}</p>
        </div>
      </div>

      <div
        v-if="isWorkerLab && activeMoment && DRAMA_MOMENTS[activeMoment]"
        class="drama-moment"
        :class="`drama-moment--${activeMoment}`"
        aria-live="assertive"
      >
        <span class="drama-moment-emoji">{{ DRAMA_MOMENTS[activeMoment].emoji }}</span>
        <span>{{ DRAMA_MOMENTS[activeMoment].label }}</span>
      </div>

      <div ref="chatRoot" class="chat" :class="{ 'chat--drama': isWorkerLab }" role="log" aria-live="polite">
        <div
          v-for="msg in thread"
          :key="msg.key"
          class="msg-row"
          :class="{
            'msg-row--user': msg.role === 'user',
            'msg-row--sys': msg.role === 'system',
            'msg-row--scene': msg.role === 'scene',
          }"
        >
          <div v-if="msg.role === 'scene'" class="scene-chapter">{{ msg.text }}</div>
          <div v-else-if="msg.role === 'time'" class="bubble bubble--time">{{ msg.text }}</div>
          <div
            v-else-if="msg.role === 'system'"
            class="bubble bubble--sys"
            :class="[
              msg.tone ? `bubble--tone-${msg.tone}` : '',
              msg.enter && isWorkerLab ? 'bubble--enter' : '',
            ]"
          >
            <span v-if="msg.source" class="bubble-source">【{{ msg.source }}】</span>
            <span>{{ msg.text }}</span>
          </div>
          <div v-else class="bubble bubble--user">
            <span class="bubble-source bubble-source--user">【你的选择】</span>
            <span>{{ msg.text }}</span>
          </div>
        </div>

        <div v-if="isWorkerLab && typingIndicator" class="typing-row" aria-live="polite">
          <div class="typing-bubble">
            <span class="typing-dots" aria-hidden="true"><i /><i /><i /></span>
            <span>{{ typingIndicator.name }}正在输入…</span>
          </div>
        </div>
      </div>

      <p v-if="isWorkerLab && sceneRevealing" class="scene-wait">消息陆续到达中…</p>

      <div v-if="currentScene && !sceneRevealing" class="opts">
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
      <p class="end-label">{{ endingHeadline }}</p>
      <p v-if="isWorkerLab && ending?.episodeCoda" class="episode-coda">{{ ending.episodeCoda }}</p>

      <div v-if="isWorkerLab" class="persona-divider" aria-hidden="true">
        <span>{{ config?.endingRevealLabel ?? '本集结算' }}</span>
      </div>

      <h1 class="h1 ending-title">{{ config?.endingSectionTitle ?? '打工人格' }}</h1>

      <div class="persona-hero">
        <div class="persona-visual" aria-hidden="true">
          <span class="persona-symbol">{{ personaVisual.symbol }}</span>
          <span class="persona-shadow" />
        </div>
        <div class="persona-copy">
          <p class="end-kicker">{{ config?.endingKicker ?? (isWorkerLab ? '今晚的你，更接近' : '你的结果是') }}</p>
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
          <span class="share-brand">{{ shareBrand }}</span>
          <span class="share-sub">{{ shareSub }}</span>
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
            <p class="share-cta">{{ shareCta }}</p>
            <p class="share-url">{{ shareUrl }}</p>
          </div>
          <span class="share-entry-btn">{{ isWorkerLab ? '进入实验室' : '进入体验馆' }}</span>
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
          <span class="reflection-title">{{ isWorkerLab ? '本集高光' : '还算扛住的地方' }}</span>
          <p>{{ ending.fitReason }}</p>
        </div>
        <div v-if="ending?.riskReason" class="reflection-card reflection-card--risk">
          <span class="reflection-title">{{ isWorkerLab ? '本集扎心' : '扎心提示' }}</span>
          <p>{{ ending.riskReason }}</p>
        </div>
      </div>

      <div class="end-actions">
        <button type="button" class="btn-secondary" @click="playAgain">
          {{ isWorkerLab ? '再看一集' : '再体验一次' }}
        </button>
        <RouterLink class="btn-outline" :to="hubPath">返回{{ hubLabel }}</RouterLink>
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

.page--drama {
  position: relative;
  background: #0f172a;
  color: #e2e8f0;
}

.page--drama::before {
  content: '';
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  opacity: 0.15;
  background-size: cover;
  background-position: center top;
  transition: background-image 0.6s ease, opacity 0.4s ease;
}

.page--dev-desk::before {
  background-image:
    linear-gradient(180deg, rgba(15, 23, 42, 0.55), rgba(15, 23, 42, 0.92)),
    radial-gradient(ellipse at 70% 20%, rgba(99, 102, 241, 0.35), transparent 50%),
    radial-gradient(ellipse at 20% 80%, rgba(30, 58, 95, 0.5), transparent 45%);
}

.page--dev-alert-desk::before {
  background-image:
    linear-gradient(180deg, rgba(69, 10, 10, 0.35), rgba(15, 23, 42, 0.92)),
    radial-gradient(ellipse at 60% 30%, rgba(239, 68, 68, 0.28), transparent 55%);
}

.page--dev-meeting::before {
  background-image:
    linear-gradient(180deg, rgba(15, 23, 42, 0.5), rgba(15, 23, 42, 0.94)),
    radial-gradient(ellipse at 50% 0%, rgba(148, 163, 184, 0.25), transparent 60%);
}

.page--dev-night-office::before {
  background-image:
    linear-gradient(180deg, rgba(15, 23, 42, 0.35), rgba(2, 6, 23, 0.96)),
    radial-gradient(ellipse at 80% 70%, rgba(59, 130, 246, 0.22), transparent 50%);
}

.page--hr-office::before,
.page--hr-inbox::before {
  background-image:
    linear-gradient(180deg, rgba(30, 27, 75, 0.45), rgba(15, 23, 42, 0.94)),
    radial-gradient(ellipse at 40% 30%, rgba(168, 85, 247, 0.2), transparent 55%);
}

.page--hr-meeting::before {
  background-image:
    linear-gradient(180deg, rgba(49, 46, 129, 0.4), rgba(15, 23, 42, 0.95)),
    radial-gradient(ellipse at 50% 10%, rgba(244, 114, 182, 0.15), transparent 50%);
}

.page--hr-night-office::before {
  background-image:
    linear-gradient(180deg, rgba(15, 23, 42, 0.4), rgba(2, 6, 23, 0.97)),
    radial-gradient(ellipse at 30% 80%, rgba(251, 113, 133, 0.18), transparent 45%);
}

.page--drama > * {
  position: relative;
  z-index: 1;
}

.top-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 12px;
}

.sound-toggle {
  flex-shrink: 0;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(15, 23, 42, 0.6);
  color: #e2e8f0;
  font-size: 16px;
  line-height: 1;
  cursor: pointer;
}

.page--drama .back {
  color: rgba(203, 213, 225, 0.85);
}

.page--drama .back:hover {
  color: #fda4af;
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

.play--drama {
  position: relative;
  isolation: isolate;
}

/* 聊天区上方：场景镜头条（语义图标 + 标签） */
.scene-cine {
  position: relative;
  z-index: 1;
  flex-shrink: 0;
  display: flex;
  align-items: stretch;
  min-height: 88px;
  margin-bottom: 12px;
  border-radius: 14px;
  overflow: hidden;
  border: 1px solid rgba(148, 163, 184, 0.28);
  box-shadow: 0 10px 28px rgba(0, 0, 0, 0.4);
  transition:
    border-color 0.4s ease,
    box-shadow 0.4s ease;
}

.scene-cine--revealing {
  box-shadow: 0 10px 32px rgba(99, 102, 241, 0.22);
}

.scene-cine--alert {
  background: linear-gradient(120deg, #7f1d1d 0%, #312e81 55%, #0f172a 100%);
}

.scene-cine--meeting {
  background: linear-gradient(120deg, #4338ca 0%, #1e3a5f 50%, #0f172a 100%);
}

.scene-cine--chaos {
  background: linear-gradient(120deg, #b91c1c 0%, #4c1d95 50%, #0f172a 100%);
}

.scene-cine--night {
  background: linear-gradient(120deg, #0369a1 0%, #1e1b4b 55%, #020617 100%);
}

.scene-cine--life {
  background: linear-gradient(120deg, #9d174d 0%, #4c1d95 50%, #0f172a 100%);
}

.scene-cine--inbox {
  background: linear-gradient(120deg, #6d28d9 0%, #334155 50%, #0f172a 100%);
}

.scene-cine--emotion {
  background: linear-gradient(120deg, #7e22ce 0%, #4338ca 50%, #0f172a 100%);
}

.scene-cine--pressure {
  background: linear-gradient(120deg, #475569 0%, #1e293b 55%, #020617 100%);
}

.scene-cine--default {
  background: linear-gradient(120deg, #475569 0%, #1e293b 55%, #0f172a 100%);
}

.scene-cine-art {
  position: relative;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 96px;
  min-height: 88px;
  overflow: hidden;
  background: rgba(0, 0, 0, 0.28);
  border-right: 1px solid rgba(255, 255, 255, 0.1);
}

.scene-cine-glow {
  position: absolute;
  inset: 0;
  background: radial-gradient(circle at 50% 45%, rgba(255, 255, 255, 0.22) 0%, transparent 62%);
  pointer-events: none;
}

.scene-cine-art :deep(.scene-cine-icon) {
  position: relative;
  z-index: 1;
}

.scene-cine-copy {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 6px;
  padding: 14px 16px;
  min-width: 0;
}

.scene-cine-tag {
  display: inline-flex;
  align-self: flex-start;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.06em;
  text-transform: none;
  color: #e2e8f0;
  background: rgba(15, 23, 42, 0.45);
  border: 1px solid rgba(255, 255, 255, 0.14);
}

.scene-cine-title {
  margin: 0;
  font-size: 15px;
  font-weight: 800;
  line-height: 1.35;
  letter-spacing: 0.02em;
  color: #f8fafc;
  text-shadow: 0 2px 12px rgba(0, 0, 0, 0.5);
}

.drama-moment {
  position: absolute;
  top: 8px;
  right: 8px;
  z-index: 4;
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.88);
  border: 1px solid rgba(251, 113, 133, 0.45);
  color: #fecdd3;
  font-size: 13px;
  font-weight: 700;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.35);
  animation: moment-pop 0.35s ease;
}

.drama-moment--ticket-red {
  border-color: rgba(239, 68, 68, 0.55);
  color: #fecaca;
}

.drama-moment--call-incoming {
  animation: moment-shake 0.5s ease, moment-pop 0.35s ease;
}

.drama-moment-emoji {
  font-size: 18px;
}

@keyframes moment-pop {
  from {
    opacity: 0;
    transform: translateY(-8px) scale(0.92);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes moment-shake {
  0%,
  100% {
    transform: translateX(0);
  }
  25% {
    transform: translateX(-4px);
  }
  75% {
    transform: translateX(4px);
  }
}

.scene-chapter {
  width: 100%;
  margin: 10px 0 16px;
  padding: 10px 14px;
  text-align: center;
  font-size: 13px;
  font-weight: 800;
  letter-spacing: 0.08em;
  color: #fecdd3;
  background: rgba(15, 23, 42, 0.72);
  border: 1px solid rgba(251, 113, 133, 0.28);
  border-radius: 999px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
  animation: chapter-in 0.45s ease;
}

@keyframes chapter-in {
  from {
    opacity: 0;
    transform: translateY(6px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.scene-wait {
  margin: 0 0 10px;
  font-size: 12px;
  color: rgba(203, 213, 225, 0.7);
  text-align: center;
}

.typing-row {
  display: flex;
  justify-content: flex-start;
  margin-bottom: 8px;
}

.typing-bubble {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border-radius: 14px;
  background: rgba(30, 41, 59, 0.85);
  border: 1px solid rgba(148, 163, 184, 0.3);
  font-size: 12px;
  color: rgba(203, 213, 225, 0.9);
}

.typing-dots {
  display: inline-flex;
  gap: 3px;
}

.typing-dots i {
  width: 5px;
  height: 5px;
  border-radius: 50%;
  background: #94a3b8;
  animation: typing-bounce 1s infinite ease-in-out;
}

.typing-dots i:nth-child(2) {
  animation-delay: 0.15s;
}

.typing-dots i:nth-child(3) {
  animation-delay: 0.3s;
}

@keyframes typing-bounce {
  0%,
  80%,
  100% {
    transform: translateY(0);
    opacity: 0.45;
  }
  40% {
    transform: translateY(-4px);
    opacity: 1;
  }
}

.chat--drama {
  position: relative;
  z-index: 2;
  background: rgba(15, 23, 42, 0.58);
  border-color: rgba(148, 163, 184, 0.28);
  backdrop-filter: blur(14px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.35);
}

.play--drama .opts {
  position: relative;
  z-index: 2;
}

.page--drama .bubble--sys {
  background: rgba(30, 41, 59, 0.92);
  border-color: rgba(148, 163, 184, 0.32);
  color: #e2e8f0;
}

.page--drama .bubble-source {
  color: #94a3b8;
}

.bubble--tone-life {
  border-color: rgba(251, 191, 36, 0.35);
  box-shadow: inset 0 0 0 1px rgba(251, 191, 36, 0.12);
}

.bubble--tone-private {
  border-color: rgba(96, 165, 250, 0.35);
}

.bubble--tone-alert {
  border-color: rgba(248, 113, 113, 0.45);
  background: rgba(69, 10, 10, 0.35);
}

.bubble--tone-call {
  border-color: rgba(52, 211, 153, 0.35);
}

.bubble--enter {
  animation: bubble-in 0.32s ease;
}

@keyframes bubble-in {
  from {
    opacity: 0;
    transform: translateY(10px) scale(0.97);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

.page--drama .stat-pill {
  background: rgba(15, 23, 42, 0.55);
  border-color: rgba(148, 163, 184, 0.28);
  color: #e2e8f0;
}

.page--drama .stat-l {
  color: rgba(203, 213, 225, 0.75);
}

.page--drama .stat-v {
  color: #f8fafc;
}

.page--drama .opt-btn {
  background: rgba(30, 41, 59, 0.9);
  border-color: rgba(148, 163, 184, 0.35);
  color: #f1f5f9;
}

.page--drama .opt-btn:hover {
  border-color: rgba(251, 113, 133, 0.5);
  background: rgba(49, 46, 129, 0.55);
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

/* 连续剧模式优先：避免与 page--heavy 叠加后气泡变白、文字变浅 */
.page--drama.page--heavy .chat,
.page--drama.page--tense .chat,
.page--drama .chat.chat--drama {
  background: rgba(15, 23, 42, 0.72);
  border-color: rgba(148, 163, 184, 0.28);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.04);
}

.page--drama.page--heavy .bubble--sys,
.page--drama.page--tense .bubble--sys,
.page--drama .bubble--sys {
  background: rgba(30, 41, 59, 0.92);
  border-color: rgba(148, 163, 184, 0.32);
  color: #e2e8f0;
}

.page--drama.page--heavy .bubble-source,
.page--drama.page--tense .bubble-source,
.page--drama .bubble-source {
  color: #94a3b8;
}

.page--drama.page--heavy .bubble--user,
.page--drama.page--tense .bubble--user,
.page--drama .bubble--user {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.35), rgba(168, 85, 247, 0.28));
  border-color: rgba(129, 140, 248, 0.45);
  color: #f8fafc;
}

.page--drama.page--heavy .bubble-source--user,
.page--drama .bubble-source--user {
  color: #c4b5fd;
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

.intro-episode {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 700;
  color: #7c3aed;
  letter-spacing: 0.04em;
}

.end-label {
  margin: 0;
  font-size: 13px;
  font-weight: 800;
  color: #5b21b6;
}

.episode-coda {
  margin: 14px 0 0;
  font-size: 15px;
  line-height: 1.75;
  color: var(--text);
  white-space: pre-line;
}

.persona-divider {
  margin: 22px 0 4px;
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  text-transform: uppercase;
}

.persona-divider::before,
.persona-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(99, 102, 241, 0.35), transparent);
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
