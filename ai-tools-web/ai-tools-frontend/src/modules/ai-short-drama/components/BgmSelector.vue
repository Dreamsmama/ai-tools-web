<script setup>
import { computed } from 'vue'
import {
  BGM_MODE_OPTIONS,
  BGM_TRACKS,
  DEFAULT_BGM_FILE,
  suggestBgmFile,
  bgmTrackLabel,
} from '../data/bgmOptions.js'

const bgmMode = defineModel('bgmMode', { type: String, default: 'auto' })
const bgmFile = defineModel('bgmFile', { type: String, default: DEFAULT_BGM_FILE })

// 确保手动模式默认值落在现有曲目上
if (!BGM_TRACKS.some((t) => t.file === bgmFile.value)) {
  bgmFile.value = DEFAULT_BGM_FILE
}

const props = defineProps({
  emotionStyle: { type: String, default: '' },
})

const previewFile = computed(() => {
  if (bgmMode.value === 'manual') return bgmFile.value
  if (bgmMode.value === 'auto') return suggestBgmFile(props.emotionStyle)
  return ''
})

const previewUrl = computed(() =>
  previewFile.value ? `/short-drama/bgm/${previewFile.value}` : '',
)

const autoHint = computed(() => {
  const file = suggestBgmFile(props.emotionStyle)
  return props.emotionStyle
    ? `预计匹配：${bgmTrackLabel(file)}（${props.emotionStyle}）`
    : `预计匹配：${bgmTrackLabel(file)}（根据段落情绪）`
})
</script>

<template>
  <section class="bgm card">
    <h3 class="bgm-title">背景音乐</h3>
    <p class="bgm-desc">增强打工人情绪氛围；可在下方选择 AI 配音音色，与字幕 + 画面 + BGM 一并合成。</p>

    <div class="mode-row" role="radiogroup" aria-label="BGM 模式">
      <label
        v-for="opt in BGM_MODE_OPTIONS"
        :key="opt.value"
        class="mode-opt"
        :class="{ 'mode-opt--active': bgmMode === opt.value }"
      >
        <input v-model="bgmMode" type="radio" :value="opt.value" class="sr-only" />
        <span class="mode-opt__label">{{ opt.label }}</span>
        <span class="mode-opt__hint">{{ opt.hint }}</span>
      </label>
    </div>

    <p v-if="bgmMode === 'auto'" class="auto-hint">{{ autoHint }}</p>

    <div v-if="bgmMode !== 'none' && previewUrl" class="preview">
      <span class="preview-label">试听 BGM</span>
      <audio :src="previewUrl" controls preload="metadata" class="preview-audio" />
      <p class="preview-tip">已使用你放入的 Atlas Audio 曲目；合成前可先试听确认。</p>
    </div>

    <label v-if="bgmMode === 'manual'" class="manual-field">
      <span class="manual-label">选择曲目</span>
      <select v-model="bgmFile" class="manual-select">
        <option v-for="t in BGM_TRACKS" :key="t.file" :value="t.file">
          {{ t.label }}
        </option>
      </select>
    </label>
  </section>
</template>

<style scoped>
.bgm {
  padding: 16px;
}

.card {
  background: var(--surface-solid);
  border-radius: var(--radius);
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
}

.bgm-title {
  margin: 0 0 6px;
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
}

.bgm-desc {
  margin: 0 0 14px;
  font-size: 12px;
  line-height: 1.55;
  color: var(--text-muted);
}

.mode-row {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.mode-opt {
  display: flex;
  flex-direction: column;
  gap: 2px;
  padding: 10px 12px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  cursor: pointer;
  transition:
    border-color var(--transition),
    background var(--transition);
}

.mode-opt--active {
  border-color: rgba(99, 102, 241, 0.45);
  background: rgba(99, 102, 241, 0.08);
}

.mode-opt__label {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
}

.mode-opt__hint {
  font-size: 11px;
  color: var(--text-muted);
}

.auto-hint {
  margin: 12px 0 0;
  font-size: 12px;
  font-weight: 600;
  color: #5b21b6;
}

.manual-field {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-top: 12px;
}

.manual-label {
  font-size: 13px;
  font-weight: 600;
  color: var(--text);
}

.manual-select {
  width: 100%;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  font-size: 14px;
  background: rgba(255, 255, 255, 0.9);
}

.preview {
  margin-top: 12px;
  padding: 12px;
  border-radius: 12px;
  background: rgba(99, 102, 241, 0.06);
  border: 1px solid rgba(99, 102, 241, 0.15);
}

.preview-label {
  display: block;
  font-size: 12px;
  font-weight: 700;
  color: var(--text);
  margin-bottom: 8px;
}

.preview-audio {
  width: 100%;
  height: 36px;
}

.preview-tip {
  margin: 8px 0 0;
  font-size: 11px;
  line-height: 1.5;
  color: var(--text-muted);
}

.preview-tip code {
  font-size: 10px;
}

.guide-toggle {
  margin-top: 12px;
  padding: 0;
  border: none;
  background: none;
  font-size: 12px;
  font-weight: 700;
  color: #6366f1;
  cursor: pointer;
  text-align: left;
}

.guide-toggle:hover {
  color: #4f46e5;
}

.guide {
  margin-top: 10px;
  padding: 12px;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.03);
  border: 1px solid rgba(148, 163, 184, 0.25);
  font-size: 12px;
  line-height: 1.55;
  color: var(--text-muted);
}

.guide-lead {
  margin: 0 0 10px;
  color: var(--text);
}

.guide-lead strong {
  font-weight: 700;
}

.guide code {
  font-size: 11px;
}

.source-list {
  margin: 0 0 12px;
  padding-left: 18px;
}

.source-list li {
  margin-bottom: 6px;
}

.source-list a {
  font-weight: 600;
  color: #6366f1;
  text-decoration: none;
}

.source-list a:hover {
  text-decoration: underline;
}

.source-note {
  display: block;
  font-size: 11px;
  color: var(--text-muted);
}

.map-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
  margin-bottom: 10px;
}

.map-table th,
.map-table td {
  padding: 6px 8px;
  text-align: left;
  border-bottom: 1px solid rgba(148, 163, 184, 0.2);
  vertical-align: top;
}

.map-table th {
  font-weight: 700;
  color: var(--text);
}

.map-table code {
  font-size: 10px;
  word-break: break-all;
}

.guide-foot {
  margin: 0;
  font-size: 11px;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}
</style>
