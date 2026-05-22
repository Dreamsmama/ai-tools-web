<script setup>
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import BgmSelector from './BgmSelector.vue'
import { DEFAULT_BGM_FILE, bgmTrackLabel } from '../data/bgmOptions.js'
import {
  hasUsableMaterial,
  materialDisplayMessage,
  MISSING_MATERIAL_MSG,
} from '../lib/materialFallback.js'

const props = defineProps({
  result: { type: Object, required: true },
  videoLoading: { type: Boolean, default: false },
  videoUrl: { type: String, default: '' },
  bgmUsed: { type: String, default: '' },
})

const bgmMode = defineModel('bgmMode', { type: String, default: 'auto' })
const bgmFile = defineModel('bgmFile', { type: String, default: DEFAULT_BGM_FILE })
const voiceId = defineModel('voiceId', { type: String, default: '' })

const VOICE_OPTIONS = [
  { id: '', label: '无配音' },
  { id: 'longxiaochun_v2', label: '女声·温柔' },
  { id: 'longwan', label: '女声·播报' },
  { id: 'longhua', label: '男声·沉稳' },
  { id: 'longshuo', label: '男声·年轻' },
]

defineEmits(['regenerate', 'edit', 'copyJson', 'copyFullText', 'renderVideo'])

const displaySegments = computed(() => {
  if (props.result?.segments?.length) {
    return props.result.segments
  }
  return (props.result?.shots || []).map((s) => ({
    segmentNo: s.shotNo,
    duration: s.duration,
    text: s.subtitle,
    role: s.role,
    emotion: s.emotion,
    scene: s.scene,
    imageTags: s.imageTags || [],
    contentType: s.contentType || s.material?.contentType,
    material: s.material,
  }))
})

const fullCopyText = computed(() =>
  displaySegments.value.map((s) => s.text).join('\n'),
)

const estimatedDurationSeconds = computed(() => {
  const fromApi = props.result?.estimatedDurationSeconds
  if (fromApi && fromApi > 0) return fromApi
  const sum = displaySegments.value.reduce((acc, s) => acc + Number(s.duration || 0), 0)
  return sum > 0 ? sum : null
})

function materialSourceLabel(seg) {
  const m = seg.material
  if (!hasUsableMaterial(m)) return '缺少素材'
  if (m.aiGenerated) return m.cacheHit ? 'AI 缓存' : 'AI 生成'
  if (m.source === 'cache') return '缓存命中'
  if (m.source === 'generated') return 'AI 生成'
  if (m.source === 'character_ip') return '角色IP'
  return '素材库'
}

function segmentMissingMessage(seg) {
  return materialDisplayMessage(seg.material) || MISSING_MATERIAL_MSG
}

const CONTENT_TYPE_LABELS = {
  monologue: '情绪独白',
  career: '职业描述',
  dialogue: '工作沟通',
  crisis: '崩溃压抑',
  ending: '总结结尾',
}

function contentTypeLabel(seg) {
  const key = seg.contentType || seg.material?.contentType
  return CONTENT_TYPE_LABELS[key] || key || '—'
}

const MATERIAL_TYPE_LABELS = {
  character: 'character · 人物',
  scene: 'scene · 场景',
  ui: 'ui · 界面',
  effect: 'effect · 氛围',
  effects: 'effect · 氛围',
  props: 'props · 道具',
}

const SLOT_TYPE_LABELS = {
  scene: '规划·场景',
  character: '规划·人物IP',
  ui: '规划·界面',
  effects: '规划·氛围',
}

function materialTypeLabel(seg) {
  const t = (seg.material?.materialType || '').toLowerCase()
  const planned = (seg.material?.plannedSlotType || '').toLowerCase()
  const actual =
    t === 'effects' ? MATERIAL_TYPE_LABELS.effects : MATERIAL_TYPE_LABELS[t] || t || '—'
  const plan = SLOT_TYPE_LABELS[planned] || (planned ? planned : '')
  if (plan && actual && actual !== '—') {
    return `${plan} → ${actual}`
  }
  return actual || plan || '—'
}
</script>

<template>
  <section class="result">
    <header class="result-head card">
      <p class="series-tag">职业观察局 · 图文成片</p>
      <h2 class="drama-title">{{ result.title }}</h2>
      <p v-if="estimatedDurationSeconds" class="duration-estimate">
        预计视频时长：{{ estimatedDurationSeconds }} 秒
        <span class="duration-estimate-hint">（由文案节奏自动计算，无需手动设置）</span>
      </p>
      <div v-if="result.characterIp" class="character-ip-banner">
        <img
          v-if="result.characterIp.baseImageUrl && result.characterIp.configured"
          :src="result.characterIp.baseImageUrl"
          :alt="result.characterIp.roleLabel"
          class="character-ip-thumb"
        />
        <div class="character-ip-text">
          <p class="character-ip-label">成片角色 IP</p>
          <p class="character-ip-role">
            {{ result.detectedCareer || result.characterIp.roleLabel }}
            <span v-if="result.characterIp.configured" class="character-ip-ok">· 已配置</span>
            <span v-else class="character-ip-warn">· 未配置</span>
          </p>
          <RouterLink
            v-if="!result.characterIp.configured"
            class="character-ip-link"
            to="/tools/ai-short-drama/characters"
          >
            去角色管理配置
          </RouterLink>
        </div>
      </div>
      <p v-if="result.source === 'mock'" class="source-hint">已使用本地模板生成（AI 暂不可用）</p>
    </header>

    <section v-if="fullCopyText" class="copy-preview card">
      <h3 class="preview-title">完整文案预览</h3>
      <pre class="preview-body">{{ fullCopyText }}</pre>
    </section>

    <ol class="segment-list">
      <li v-for="seg in displaySegments" :key="seg.segmentNo" class="segment-card card">
        <div class="segment-top">
          <span class="segment-no">段落 {{ seg.segmentNo }}</span>
          <span class="segment-duration">{{ seg.duration }}s</span>
        </div>

        <div class="segment-visual">
          <div v-if="hasUsableMaterial(seg.material)" class="segment-thumb">
            <img
              class="segment-img"
              :src="seg.material.url"
              :alt="seg.material?.name || '段落素材'"
              loading="lazy"
            />
          </div>
          <div v-else class="segment-missing">
            <p class="segment-missing-text">{{ segmentMissingMessage(seg) }}</p>
          </div>
          <p class="material-name">
            <template v-if="hasUsableMaterial(seg.material)">
              {{ seg.material?.name || '素材' }}
              <span
                class="mat-badge"
                :class="seg.material?.aiGenerated ? 'mat-badge--ai' : 'mat-badge--src'"
              >
                {{ materialSourceLabel(seg) }}
              </span>
            </template>
            <span v-else class="mat-badge mat-badge--warn">{{ materialSourceLabel(seg) }}</span>
          </p>
          <p v-if="seg.material?.imageWidth" class="material-debug">
            {{ seg.material.imageWidth }}×{{ seg.material.imageHeight }}
            · {{ seg.material.aspectRatio }}
            · {{ seg.material.isVertical ? '竖屏' : '横图' }}
          </p>
        </div>

        <p class="segment-text">{{ seg.text }}</p>

        <dl class="segment-meta">
          <div><dt>文案类型</dt><dd>{{ contentTypeLabel(seg) }}</dd></div>
          <div><dt>素材类型</dt><dd>{{ materialTypeLabel(seg) }}</dd></div>
          <div><dt>情绪</dt><dd>{{ seg.emotion }}</dd></div>
          <div><dt>场景</dt><dd>{{ seg.scene }}</dd></div>
          <div><dt>角色</dt><dd>{{ seg.role }}</dd></div>
          <div v-if="seg.sceneDescriptionSource">
            <dt>场景描述来源</dt>
            <dd>
              <span v-if="seg.sceneDescriptionSource === 'llm'" class="source-badge source-badge--llm">AI 生成</span>
              <span v-else-if="seg.sceneDescriptionSource === 'dedup_rewrite'" class="source-badge source-badge--dedup">↻ 去重改写</span>
              <span v-else class="source-badge source-badge--fallback">⚠ 兜底模板</span>
            </dd>
          </div>
        </dl>

        <p v-if="seg.sceneDescription" class="scene-description">
          <span class="scene-description-label">场景描述：</span>{{ seg.sceneDescription }}
        </p>

        <p class="tags">
          <span v-for="tag in seg.imageTags" :key="tag" class="tag">{{ tag }}</span>
        </p>
      </li>
    </ol>

    <section v-if="videoUrl" class="video-panel card">
      <h3 class="video-title">竖屏图文成片预览</h3>
      <p v-if="bgmUsed" class="bgm-used">背景音乐：{{ bgmTrackLabel(bgmUsed) }}</p>
      <video class="video-player" :src="videoUrl" controls playsinline />
      <a class="video-download" :href="videoUrl" download>下载 MP4</a>
    </section>

    <BgmSelector
      v-model:bgm-mode="bgmMode"
      v-model:bgm-file="bgmFile"
      :emotion-style="result.emotionStyle || ''"
    />

    <div class="voice-selector card">
      <label class="voice-label">配音音色</label>
      <div class="voice-options">
        <button
          v-for="opt in VOICE_OPTIONS"
          :key="opt.id"
          type="button"
          class="voice-opt"
          :class="{ active: voiceId === opt.id }"
          @click="voiceId = opt.id"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <div class="actions">
      <button
        type="button"
        class="btn-video btn-gradient"
        :disabled="videoLoading"
        @click="$emit('renderVideo')"
      >
        {{ videoLoading ? (voiceId ? '正在合成视频（配音+BGM）…' : '正在合成视频（字幕+BGM）…') : '生成图文成片视频' }}
      </button>
      <button type="button" class="btn-secondary" @click="$emit('edit')">修改条件</button>
      <button type="button" class="btn-secondary" @click="$emit('copyFullText')">复制完整文案</button>
      <button type="button" class="btn-secondary" @click="$emit('copyJson')">复制 JSON</button>
      <button type="button" class="btn-primary btn-gradient" @click="$emit('regenerate')">重新生成</button>
    </div>

    <p class="future-note">
      适合抖音 / 小红书 / B站：一句文案一张图 + 情绪 BGM{{ voiceId ? ' + AI 配音（画面时长随朗读对齐）' : '' }}
    </p>
  </section>
</template>

<style scoped>
.result {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.card {
  background: var(--surface-solid);
  border-radius: var(--radius);
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
}

.result-head {
  padding: 18px 16px;
}

.series-tag {
  margin: 0 0 8px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #6366f1;
}

.drama-title {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  line-height: 1.35;
  color: var(--text);
}

.duration-estimate {
  margin: 10px 0 0;
  font-size: 14px;
  font-weight: 700;
  color: #4f46e5;
}

.duration-estimate-hint {
  display: block;
  margin-top: 4px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-muted);
}

.character-ip-banner {
  display: flex;
  gap: 12px;
  align-items: center;
  margin-top: 12px;
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.character-ip-thumb {
  width: 48px;
  height: 72px;
  object-fit: cover;
  border-radius: 8px;
  flex-shrink: 0;
}

.character-ip-label {
  margin: 0 0 2px;
  font-size: 11px;
  font-weight: 700;
  color: #6366f1;
}

.character-ip-role {
  margin: 0;
  font-size: 14px;
  font-weight: 700;
}

.character-ip-ok {
  color: #047857;
  font-weight: 600;
}

.character-ip-warn {
  color: #b45309;
  font-weight: 600;
}

.character-ip-link {
  display: inline-block;
  margin-top: 6px;
  font-size: 12px;
  font-weight: 700;
  color: #4f46e5;
  text-decoration: none;
}

.source-hint {
  margin: 10px 0 0;
  font-size: 12px;
  color: #b45309;
}

.copy-preview {
  padding: 16px;
}

.preview-title {
  margin: 0 0 10px;
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
}

.preview-body {
  margin: 0;
  font-size: 14px;
  line-height: 1.75;
  white-space: pre-wrap;
  color: var(--text);
  font-family: inherit;
}

.segment-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.segment-card {
  padding: 16px;
  overflow: hidden;
}

.segment-top {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.segment-no {
  font-size: 14px;
  font-weight: 800;
  color: #5b21b6;
}

.segment-duration {
  font-size: 12px;
  font-weight: 600;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.1);
  color: #4f46e5;
}

.segment-visual {
  margin-bottom: 12px;
}

.segment-thumb {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 120px;
  max-height: 280px;
  padding: 8px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: linear-gradient(180deg, #f8fafc 0%, #eef2ff 100%);
  overflow: hidden;
}

.segment-img {
  display: block;
  max-width: 100%;
  max-height: 264px;
  width: auto;
  height: auto;
  object-fit: contain;
  border-radius: 6px;
}

.material-name {
  margin: 8px 0 0;
  font-size: 12px;
  color: var(--text-muted);
}

.material-debug {
  margin: 4px 0 0;
  font-size: 11px;
  font-weight: 600;
  color: #6366f1;
  font-family: ui-monospace, monospace;
}

.mat-badge {
  display: inline-block;
  margin-left: 6px;
  padding: 2px 6px;
  border-radius: 6px;
  font-size: 10px;
  font-weight: 700;
}

.mat-badge--ai {
  background: rgba(16, 185, 129, 0.15);
  color: #047857;
}

.mat-badge--src {
  background: rgba(99, 102, 241, 0.12);
  color: #4f46e5;
}

.segment-missing {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 160px;
  padding: 20px 16px;
  border-radius: 12px;
  background: repeating-linear-gradient(
    -45deg,
    rgba(99, 102, 241, 0.06),
    rgba(99, 102, 241, 0.06) 8px,
    rgba(148, 163, 184, 0.08) 8px,
    rgba(148, 163, 184, 0.08) 16px
  );
  border: 1px dashed rgba(99, 102, 241, 0.35);
}

.segment-missing-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  text-align: center;
  color: #64748b;
  font-weight: 600;
}

.mat-badge--warn {
  background: rgba(245, 158, 11, 0.15);
  color: #b45309;
}

.segment-text {
  margin: 0 0 12px;
  font-size: 16px;
  line-height: 1.55;
  font-weight: 600;
  color: var(--text);
}

.segment-meta {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px 12px;
  margin: 0 0 12px;
}

.segment-meta dt {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  margin: 0;
}

.segment-meta dd {
  margin: 2px 0 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text);
}

.scene-description {
  margin: 6px 0 0;
  font-size: 12px;
  color: #64748b;
  line-height: 1.6;
  background: rgba(241, 245, 249, 0.8);
  border-radius: 8px;
  padding: 8px 10px;
}

.scene-description-label {
  font-weight: 600;
  color: #475569;
  margin-right: 4px;
}

.source-badge {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 6px;
  font-weight: 600;
}

.source-badge--llm {
  background: rgba(16, 185, 129, 0.12);
  color: #059669;
}

.source-badge--fallback {
  background: rgba(245, 158, 11, 0.12);
  color: #d97706;
}

.source-badge--dedup {
  background: rgba(26, 115, 232, 0.1);
  color: #1a73e8;
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 0;
}

.tag {
  font-size: 11px;
  padding: 4px 8px;
  border-radius: 6px;
  background: rgba(15, 23, 42, 0.06);
  color: #475569;
  font-family: ui-monospace, monospace;
}

.video-panel {
  padding: 16px;
}

.video-title {
  margin: 0 0 12px;
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
}

.bgm-used {
  margin: 0 0 10px;
  font-size: 12px;
  font-weight: 600;
  color: #5b21b6;
}

.video-player {
  width: 100%;
  max-height: 420px;
  border-radius: 14px;
  background: #0f172a;
  border: 1px solid rgba(148, 163, 184, 0.3);
}

.video-download {
  display: inline-block;
  margin-top: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #6366f1;
  text-decoration: none;
}

.video-download:hover {
  color: #4f46e5;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.btn-video {
  width: 100%;
  min-width: 100%;
  padding: 14px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  border: none;
  color: #fff;
  cursor: pointer;
}

.btn-video:disabled {
  opacity: 0.75;
  cursor: not-allowed;
}

.btn-secondary,
.btn-primary {
  flex: 1;
  min-width: calc(50% - 4px);
  padding: 12px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  border: 1px solid rgba(99, 102, 241, 0.28);
  background: rgba(255, 255, 255, 0.9);
  color: #5b21b6;
}

.btn-primary {
  min-width: 100%;
  border: none;
  color: #fff;
}

.future-note {
  margin: 0;
  padding: 12px 14px;
  font-size: 11px;
  line-height: 1.6;
  color: var(--text-muted);
  border-radius: var(--radius-sm);
  background: rgba(99, 102, 241, 0.06);
  border: 1px dashed rgba(99, 102, 241, 0.2);
}

.voice-selector {
  padding: 14px 16px;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.voice-label {
  font-size: 13px;
  font-weight: 700;
  color: var(--text-muted);
}

.voice-options {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.voice-opt {
  padding: 7px 14px;
  border-radius: 20px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  border: 1.5px solid rgba(99, 102, 241, 0.25);
  background: rgba(255, 255, 255, 0.85);
  color: #475569;
  transition: all 0.15s ease;
}

.voice-opt:hover {
  border-color: rgba(99, 102, 241, 0.55);
  color: #4f46e5;
}

.voice-opt.active {
  background: rgba(99, 102, 241, 0.12);
  border-color: #6366f1;
  color: #4f46e5;
}
</style>
