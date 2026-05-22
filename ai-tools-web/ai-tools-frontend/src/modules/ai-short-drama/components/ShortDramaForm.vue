<script setup>
import { computed, onMounted } from 'vue'
import CharacterIpPreview from './CharacterIpPreview.vue'
import {
  CAREER_OPTION_AUTO,
  EMOTION_STYLE_OPTIONS,
  INPUT_MODES,
  SCRIPT_PLACEHOLDER,
  THEME_SUGGESTIONS,
} from '../data/options.js'
import { useProfessionStore } from '../stores/professionStore.js'

const form = defineModel({ type: Object, required: true })
defineProps({
  loading: { type: Boolean, default: false },
})
defineEmits(['submit'])

const { ensureLoaded, careerOptions } = useProfessionStore()
const careerList = computed(() => careerOptions())

onMounted(() => {
  ensureLoaded()
})

const isScriptMode = () => form.value.input_mode !== 'ai'

function applyThemeSuggestion(text) {
  form.value.theme = text
}

function switchMode(mode) {
  form.value.input_mode = mode
  if (mode === 'ai') {
    if (!form.value.career && careerList.value.length) {
      form.value.career = careerList.value[0]
    }
    if (!form.value.emotion_style) {
      form.value.emotion_style = EMOTION_STYLE_OPTIONS[0]
    }
  }
}
</script>

<template>
  <form class="form card" @submit.prevent="$emit('submit')">
    <fieldset class="mode-switch">
      <legend class="label">输入模式</legend>
      <div class="mode-tabs" role="tablist">
        <button
          v-for="m in INPUT_MODES"
          :key="m.value"
          type="button"
          role="tab"
          class="mode-tab"
          :class="{ 'mode-tab--active': form.input_mode === m.value }"
          :aria-selected="form.input_mode === m.value"
          @click="switchMode(m.value)"
        >
          <span class="mode-tab__label">{{ m.label }}</span>
          <span class="mode-tab__hint">{{ m.hint }}</span>
        </button>
      </div>
    </fieldset>

    <template v-if="isScriptMode()">
      <label class="field field--script">
        <span class="label">输入职业观察局文案</span>
        <p class="field-hint">粘贴你已写好的完整文案，系统将自动识别职业、拆段并匹配配图。</p>
        <textarea
          v-model="form.script"
          class="input input--script"
          rows="14"
          :placeholder="SCRIPT_PLACEHOLDER"
          required
        />
      </label>

      <label class="field">
        <span class="label">职业角色 <span class="optional">（可选，识别失败时手动指定）</span></span>
        <select v-model="form.career" class="input">
          <option :value="CAREER_OPTION_AUTO">自动识别</option>
          <option v-for="c in careerList" :key="c" :value="c">{{ c }}</option>
        </select>
      </label>

      <CharacterIpPreview :career="form.career" />

      <p class="material-hint">
        场景配图由 AI 按文案逐段生成（需配置 <code>JIMENG_API_KEY</code>），长文案约 10～20 分钟，请耐心等待勿关闭页面。
      </p>
    </template>

    <template v-else>
      <label class="field">
        <span class="label">职业角色</span>
        <select v-model="form.career" class="input" required>
          <option v-for="c in careerList" :key="c" :value="c">{{ c }}</option>
        </select>
      </label>

      <label class="field">
        <span class="label">主题</span>
        <input
          v-model="form.theme"
          class="input"
          type="text"
          maxlength="80"
          placeholder="例如：夹在中间、上线前改需求"
          required
        />
        <div class="chips" role="list">
          <button
            v-for="t in THEME_SUGGESTIONS"
            :key="t"
            type="button"
            class="chip"
            role="listitem"
            @click="applyThemeSuggestion(t)"
          >
            {{ t }}
          </button>
        </div>
      </label>

      <label class="field">
        <span class="label">情绪风格</span>
        <select v-model="form.emotion_style" class="input" required>
          <option v-for="e in EMOTION_STYLE_OPTIONS" :key="e" :value="e">{{ e }}</option>
        </select>
      </label>

      <CharacterIpPreview :career="form.career" />
    </template>

    <button type="submit" class="submit btn-gradient" :disabled="loading">
      {{
        loading
          ? isScriptMode()
            ? '正在分析文案并匹配素材…'
            : '正在生成文案并匹配素材…'
          : '生成分镜'
      }}
    </button>
  </form>
</template>

<style scoped>
.form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card {
  background: var(--surface-solid);
  border-radius: var(--radius);
  padding: 18px 16px;
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
}

.mode-switch {
  border: none;
  margin: 0;
  padding: 0;
}

.mode-tabs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.mode-tab {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 4px;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(255, 255, 255, 0.85);
  cursor: pointer;
  text-align: left;
  transition:
    border-color var(--transition),
    background var(--transition),
    box-shadow var(--transition);
}

.mode-tab--active {
  border-color: rgba(99, 102, 241, 0.45);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.08));
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.mode-tab__label {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
}

.mode-tab__hint {
  font-size: 11px;
  line-height: 1.45;
  color: var(--text-muted);
}

.field {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.field--script {
  gap: 6px;
}

.field-hint {
  margin: 0;
  font-size: 12px;
  line-height: 1.5;
  color: var(--text-muted);
}

.label {
  font-size: 13px;
  font-weight: 700;
  color: var(--text);
}

.optional {
  font-weight: 500;
  color: var(--text-muted);
}

.input {
  width: 100%;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  font-size: 15px;
  color: var(--text);
  background: rgba(255, 255, 255, 0.9);
  font-family: inherit;
}

.input--script {
  min-height: 280px;
  line-height: 1.65;
  resize: vertical;
  font-size: 14px;
}

.input:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.5);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 12px;
  font-weight: 600;
  color: #5b21b6;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.08));
  border: 1px solid rgba(99, 102, 241, 0.2);
  cursor: pointer;
  transition: transform var(--transition);
}

.chip:hover {
  transform: translateY(-1px);
}

.material-hint {
  margin: 0;
  padding: 10px 12px;
  font-size: 12px;
  line-height: 1.55;
  color: var(--text-muted);
  border-radius: 12px;
  background: rgba(99, 102, 241, 0.06);
  border: 1px solid rgba(99, 102, 241, 0.12);
}

.material-hint code {
  font-size: 11px;
  padding: 1px 4px;
  border-radius: 4px;
  background: rgba(15, 23, 42, 0.06);
}

.submit {
  width: 100%;
  padding: 14px;
  border-radius: 14px;
  font-size: 16px;
  margin-top: 4px;
}

.submit:disabled {
  opacity: 0.7;
}
</style>
