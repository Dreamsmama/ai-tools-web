<script setup>
import {
  ENERGY_OPTIONS,
  FOCUS_OPTIONS,
  GO_OUT_OPTIONS,
  MOOD_OPTIONS,
  OCCUPATION_OPTIONS,
  TARGET_PERSONA_OPTIONS,
} from '../../data/lifeRpgOptions.js'

const props = defineProps({
  modelValue: { type: Object, required: true },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'submit'])

function patch(partial) {
  emit('update:modelValue', { ...props.modelValue, ...partial })
}

function toggleFocus(label) {
  const list = [...(props.modelValue.focus_directions || [])]
  const idx = list.indexOf(label)
  if (idx >= 0) list.splice(idx, 1)
  else list.push(label)
  patch({ focus_directions: list })
}

function isFocusSelected(label) {
  return (props.modelValue.focus_directions || []).includes(label)
}
</script>

<template>
  <form class="form" @submit.prevent="emit('submit')">
    <section class="card">
      <p class="field-label">我想成为怎样的人</p>
      <div class="chip-grid chip-grid--2" role="radiogroup">
        <button
          v-for="opt in TARGET_PERSONA_OPTIONS"
          :key="opt"
          type="button"
          class="chip"
          :class="{ selected: modelValue.target_persona === opt }"
          role="radio"
          :aria-checked="modelValue.target_persona === opt"
          @click="patch({ target_persona: opt })"
        >
          {{ opt }}
        </button>
      </div>
    </section>

    <section class="card">
      <p class="field-label">今天状态</p>
      <div class="chip-grid" role="radiogroup">
        <button
          v-for="opt in ENERGY_OPTIONS"
          :key="opt"
          type="button"
          class="chip"
          :class="{ selected: modelValue.energy_level === opt }"
          role="radio"
          :aria-checked="modelValue.energy_level === opt"
          @click="patch({ energy_level: opt })"
        >
          {{ opt }}
        </button>
      </div>
    </section>

    <section class="card">
      <p class="field-label">当前心情</p>
      <div class="chip-grid chip-grid--2" role="radiogroup">
        <button
          v-for="opt in MOOD_OPTIONS"
          :key="opt"
          type="button"
          class="chip"
          :class="{ selected: modelValue.mood === opt }"
          role="radio"
          :aria-checked="modelValue.mood === opt"
          @click="patch({ mood: opt })"
        >
          {{ opt }}
        </button>
      </div>
    </section>

    <section class="card">
      <p class="field-label">今天想投入的方向 <span class="hint">可多选</span></p>
      <div class="chip-grid chip-grid--2" role="group">
        <button
          v-for="opt in FOCUS_OPTIONS"
          :key="opt"
          type="button"
          class="chip chip--multi"
          :class="{ selected: isFocusSelected(opt) }"
          :aria-pressed="isFocusSelected(opt)"
          @click="toggleFocus(opt)"
        >
          {{ opt }}
        </button>
      </div>
    </section>

    <section class="card">
      <p class="field-label">今天是否想出门</p>
      <div class="chip-grid" role="radiogroup">
        <button
          v-for="opt in GO_OUT_OPTIONS"
          :key="opt"
          type="button"
          class="chip"
          :class="{ selected: modelValue.go_out === opt }"
          role="radio"
          :aria-checked="modelValue.go_out === opt"
          @click="patch({ go_out: opt })"
        >
          {{ opt }}
        </button>
      </div>
    </section>

    <section class="card">
      <p class="field-label">当前身份/职业 <span class="hint">可选</span></p>
      <div class="chip-grid chip-grid--2" role="radiogroup">
        <button
          v-for="opt in OCCUPATION_OPTIONS"
          :key="opt"
          type="button"
          class="chip"
          :class="{ selected: modelValue.occupation === opt }"
          role="radio"
          :aria-checked="modelValue.occupation === opt"
          @click="patch({ occupation: opt })"
        >
          {{ opt }}
        </button>
      </div>
    </section>

    <section class="card">
      <label class="field-label" for="life-rpg-extra">补充描述 <span class="hint">可选</span></label>
      <textarea
        id="life-rpg-extra"
        class="textarea"
        rows="3"
        placeholder="例如：最近每天上班下班很空虚，想改变但不知道从哪开始。"
        :value="modelValue.extra_notes"
        @input="patch({ extra_notes: ($event.target).value })"
      />
    </section>

    <button type="submit" class="btn btn-gradient submit-btn" :disabled="loading">
      {{ loading ? 'AI 正在生成你今天的人生副本...' : '生成我的人生副本' }}
    </button>
  </form>
</template>

<style scoped>
.form {
  display: flex;
  flex-direction: column;
}

.card {
  background: var(--surface-solid);
  border-radius: var(--radius);
  padding: 16px;
  margin-bottom: 12px;
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
}

.field-label {
  display: block;
  margin: 0 0 10px;
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
}

.hint {
  font-weight: 500;
  color: var(--text-muted);
  font-size: 12px;
}

.textarea {
  width: 100%;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(241, 245, 249, 0.85);
  font-size: 15px;
  line-height: 1.5;
  color: var(--text);
  font-family: inherit;
  resize: vertical;
  min-height: 88px;
}

.textarea:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.45);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.chip-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip-grid--2 .chip {
  flex: 1 1 calc(50% - 8px);
  min-width: calc(50% - 8px);
}

.chip {
  flex: 1 1 auto;
  min-width: fit-content;
  padding: 11px 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(255, 255, 255, 0.95);
  font-size: 14px;
  font-weight: 500;
  color: var(--text);
  text-align: center;
  transition:
    border-color var(--transition),
    background var(--transition),
    box-shadow var(--transition);
}

.chip:hover {
  border-color: rgba(99, 102, 241, 0.35);
}

.chip.selected {
  border-color: rgba(99, 102, 241, 0.55);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.08));
  box-shadow: 0 0 0 1px rgba(99, 102, 241, 0.12);
  color: #4338ca;
  font-weight: 600;
}

.chip--multi.selected::after {
  content: ' ✓';
}

.submit-btn {
  width: 100%;
  margin-top: 4px;
  padding: 15px 16px;
  border-radius: 14px;
  font-size: 16px;
}
</style>
