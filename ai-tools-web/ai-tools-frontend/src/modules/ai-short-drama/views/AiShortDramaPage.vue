<script setup>
import { onUnmounted, ref } from 'vue'
import ErrorDialog from '../../../components/ErrorDialog.vue'
import ShortDramaForm from '../components/ShortDramaForm.vue'
import ShortDramaResult from '../components/ShortDramaResult.vue'
import { CAREER_OPTION_AUTO, EMOTION_STYLE_OPTIONS } from '../data/options.js'
import { DEFAULT_BGM_FILE, DEFAULT_BGM_MODE } from '../data/bgmOptions.js'
import { requestShortDramaGenerate, requestShortDramaRenderVideo } from '../lib/shortDramaApi.js'

function createDefaultForm() {
  return {
    input_mode: 'script',
    script: '',
    career: CAREER_OPTION_AUTO,
    theme: '',
    emotion_style: EMOTION_STYLE_OPTIONS[0],
  }
}

const phase = ref(/** @type {'form'|'result'} */ ('form'))
const form = ref(createDefaultForm())
const loading = ref(false)
const loadingElapsedSec = ref(0)
let loadingTimer = null
/** @type {import('vue').Ref<object|null>} */
const result = ref(null)
const videoUrl = ref('')
const videoLoading = ref(false)
const bgmMode = ref(DEFAULT_BGM_MODE)
const bgmFile = ref(DEFAULT_BGM_FILE)
const voiceId = ref('')
const lastBgmUsed = ref('')
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

function getDisplaySegments() {
  if (result.value?.segments?.length) {
    return result.value.segments
  }
  return (result.value?.shots || []).map((s) => ({
    segmentNo: s.shotNo,
    duration: s.duration,
    text: s.subtitle,
    role: s.role,
    emotion: s.emotion,
    scene: s.scene,
    imageTags: s.imageTags || [],
    material: s.material,
  }))
}

function validateForm() {
  if (form.value.input_mode === 'script') {
    const script = (form.value.script || '').trim()
    if (!script) {
      showErrorDetail('请粘贴完整职业观察局文案。')
      return false
    }
    if (script.length < 20) {
      showErrorDetail('文案过短，请粘贴更完整的图文文案。')
      return false
    }
    return true
  }
  if (!(form.value.theme || '').trim()) {
    showErrorDetail('请填写主题。')
    return false
  }
  if (!form.value.career) {
    showErrorDetail('请选择职业角色。')
    return false
  }
  return true
}

function buildGeneratePayload() {
  const base = {
    input_mode: form.value.input_mode || 'script',
  }
  if (form.value.input_mode === 'ai') {
    return {
      ...base,
      career: form.value.career,
      theme: form.value.theme.trim(),
      emotion_style: form.value.emotion_style,
    }
  }
  const career = (form.value.career || '').trim()
  return {
    ...base,
    script: form.value.script.trim(),
    ...(career ? { career } : {}),
  }
}

function startLoadingTimer() {
  loadingElapsedSec.value = 0
  loadingTimer = window.setInterval(() => {
    loadingElapsedSec.value += 1
  }, 1000)
}

function stopLoadingTimer() {
  if (loadingTimer != null) {
    window.clearInterval(loadingTimer)
    loadingTimer = null
  }
}

onUnmounted(() => stopLoadingTimer())

async function generateStoryboard() {
  if (!validateForm()) return

  loading.value = true
  startLoadingTimer()
  const payload = buildGeneratePayload()

  try {
    const res = await requestShortDramaGenerate(payload)

    if (!res.ok) {
      const stageHint = res.stage ? `（阶段：${res.stage}）` : ''
      showErrorDetail(`${res.message}${stageHint}`)
      return
    }

    result.value = res.data
    videoUrl.value = ''
    phase.value = 'result'
  } catch (err) {
    showErrorDetail(err?.message || '生成失败，请稍后再试。')
  } finally {
    loading.value = false
    stopLoadingTimer()
  }
}

async function renderVideo() {
  const segments = getDisplaySegments()
  if (!segments.length) {
    showErrorDetail('请先生成图文段落后再合成视频。')
    return
  }

  videoLoading.value = true
  const res = await requestShortDramaRenderVideo({
    title: result.value.title || '',
    segments,
    bgm_mode: bgmMode.value,
    bgm_file: bgmMode.value === 'manual' ? bgmFile.value : undefined,
    emotion_style: result.value.emotionStyle || form.value.emotion_style || '',
    voice_id: voiceId.value || undefined,
  })
  videoLoading.value = false

  if (!res.ok) {
    showErrorDetail(res.message)
    if (res.data?.videoUrl) {
      videoUrl.value = res.data.videoUrl
    }
    return
  }

  videoUrl.value = res.data.videoUrl
  lastBgmUsed.value = res.data.bgmFile || ''
  const bgmTip = res.data.bgmFile ? `（BGM：${res.data.bgmFile}）` : ''
  const voiceTip = voiceId.value
    ? (res.data.voiceApplied ? ' + 配音' : '')
    : ''
  if (voiceId.value && !res.data.voiceApplied) {
    showErrorDetail(res.message || '配音生成失败，已改为纯BGM，请检查后端日志。')
  } else {
    const hint = res.message ? ` ${res.message}` : ''
    showToast(`视频已生成${voiceTip}${bgmTip}，可预览或下载${hint}`)
  }
}

function editConditions() {
  phase.value = 'form'
}

function buildFullText() {
  return getDisplaySegments()
    .map((s) => s.text)
    .join('\n')
}

async function copyJson() {
  if (!result.value) return
  try {
    await navigator.clipboard.writeText(JSON.stringify(result.value, null, 2))
    showToast('已复制 JSON')
  } catch {
    showToast('复制失败，请手动复制')
  }
}

async function copyFullText() {
  const text = buildFullText()
  if (!text) return
  try {
    await navigator.clipboard.writeText(text)
    showToast('已复制完整文案')
  } catch {
    showToast('复制失败，请手动复制')
  }
}

const loadingTitle = () =>
  form.value.input_mode === 'script'
    ? '正在分析文案、拆段并匹配/生成场景素材…'
    : '正在生成文案并匹配/生成场景素材…'

const loadingSub = () =>
  form.value.input_mode === 'script'
    ? '文案分析 + 逐段 AI 生图中，长文案约需 10～20 分钟，请勿关闭页面'
    : '文案生成 + 逐段 AI 生图中，长文案约需 10～20 分钟，请勿关闭页面'
</script>

<template>
  <div class="generate">
    <template v-if="phase === 'form'">
      <ShortDramaForm v-model="form" :loading="loading" @submit="generateStoryboard" />
      <div v-if="loading" class="loading-panel card" role="status">
        <p class="loading-title">{{ loadingTitle() }}</p>
        <p class="loading-sub">{{ loadingSub() }}</p>
        <p v-if="loadingElapsedSec > 0" class="loading-elapsed">
          已等待 {{ loadingElapsedSec }} 秒，后端仍在处理中，请稍候…
        </p>
      </div>
    </template>

    <template v-else-if="result">
      <ShortDramaResult
        v-model:bgm-mode="bgmMode"
        v-model:bgm-file="bgmFile"
        v-model:voice-id="voiceId"
        :result="result"
        :video-loading="videoLoading"
        :video-url="videoUrl"
        :bgm-used="lastBgmUsed"
        @regenerate="generateStoryboard"
        @edit="editConditions"
        @copy-json="copyJson"
        @copy-full-text="copyFullText"
        @render-video="renderVideo"
      />
    </template>

    <div v-if="toast" class="toast" role="status">{{ toast }}</div>
    <ErrorDialog v-model="errorDialog" :text="errorText" />
  </div>
</template>

<style scoped>
.generate {
  display: flex;
  flex-direction: column;
  gap: 0;
}

.loading-panel {
  margin-top: 12px;
  padding: 16px;
  text-align: center;
  border: 1px dashed rgba(99, 102, 241, 0.35);
  background: rgba(99, 102, 241, 0.06);
}

.loading-title {
  margin: 0 0 6px;
  font-size: 15px;
  font-weight: 700;
  color: #5b21b6;
}

.loading-sub {
  margin: 0;
  font-size: 13px;
  line-height: 1.55;
  color: var(--text-muted);
}

.loading-elapsed {
  margin: 10px 0 0;
  font-size: 12px;
  color: #7c3aed;
  font-variant-numeric: tabular-nums;
}

.card {
  background: var(--surface-solid);
  border-radius: var(--radius);
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
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
