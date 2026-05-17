<script setup>
import {
  BUDGET_OPTIONS,
  ENERGY_OPTIONS,
  GO_OUT_OPTIONS,
  INTEREST_OPTIONS,
  MOOD_OPTIONS,
  SOCIAL_OPTIONS,
} from '../../data/eveningPlanOptions.js'

const props = defineProps({
  modelValue: { type: Object, required: true },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'submit'])

function patch(partial) {
  emit('update:modelValue', { ...props.modelValue, ...partial })
}

function toggleInterest(label) {
  const list = [...(props.modelValue.interests || [])]
  const idx = list.indexOf(label)
  if (idx >= 0) list.splice(idx, 1)
  else list.push(label)
  patch({ interests: list })
}

function isInterestSelected(label) {
  return (props.modelValue.interests || []).includes(label)
}
</script>

<template>
  <form class="form" @submit.prevent="emit('submit')">
    <section class="card">
      <label class="field-label" for="evening-city">当前城市</label>
      <input
        id="evening-city"
        class="text-input"
        type="text"
        autocomplete="address-level2"
        placeholder="例如 上海、杭州、北京"
        :value="modelValue.city"
        @input="patch({ city: ($event.target).value })"
      />
    </section>

    <section class="card">
      <label class="field-label" for="evening-time">现在时间</label>
      <input
        id="evening-time"
        class="text-input"
        type="time"
        :value="modelValue.current_time"
        @input="patch({ current_time: ($event.target).value })"
      />
    </section>

    <section class="card">
      <p class="field-label">今天状态</p>
      <div class="chip-grid" role="radiogroup" aria-label="今天状态">
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
      <p class="field-label">今天心情</p>
      <div class="chip-grid" role="radiogroup" aria-label="今天心情">
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
      <p class="field-label">是否想出门</p>
      <div class="chip-grid chip-grid--2" role="radiogroup" aria-label="是否想出门">
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
      <p class="field-label">是否想社交</p>
      <div class="chip-grid chip-grid--2" role="radiogroup" aria-label="是否想社交">
        <button
          v-for="opt in SOCIAL_OPTIONS"
          :key="opt"
          type="button"
          class="chip"
          :class="{ selected: modelValue.social === opt }"
          role="radio"
          :aria-checked="modelValue.social === opt"
          @click="patch({ social: opt })"
        >
          {{ opt }}
        </button>
      </div>
    </section>

    <section class="card">
      <p class="field-label">预算</p>
      <div class="chip-grid chip-grid--2" role="radiogroup" aria-label="预算">
        <button
          v-for="opt in BUDGET_OPTIONS"
          :key="opt"
          type="button"
          class="chip"
          :class="{ selected: modelValue.budget === opt }"
          role="radio"
          :aria-checked="modelValue.budget === opt"
          @click="patch({ budget: opt })"
        >
          {{ opt }}
        </button>
      </div>
    </section>

    <section class="card">
      <p class="field-label">今天更想做什么 <span class="hint">可多选</span></p>
      <div class="chip-grid chip-grid--2" role="group" aria-label="今天更想做什么">
        <button
          v-for="opt in INTEREST_OPTIONS"
          :key="opt"
          type="button"
          class="chip chip--multi"
          :class="{ selected: isInterestSelected(opt) }"
          :aria-pressed="isInterestSelected(opt)"
          @click="toggleInterest(opt)"
        >
          {{ opt }}
        </button>
      </div>
    </section>

    <section class="card">
      <label class="field-label" for="evening-extra">额外补充 <span class="hint">可选</span></label>
      <textarea
        id="evening-extra"
        class="textarea"
        rows="3"
        placeholder="例如：不想太累、明天还要早起、想吃热乎的"
        :value="modelValue.extra_notes"
        @input="patch({ extra_notes: ($event.target).value })"
      />
    </section>

    <button type="submit" class="btn btn-gradient submit-btn" :disabled="loading">
      {{ loading ? '正在根据你的状态安排今晚...' : 'AI 帮我安排今晚' }}
    </button>
  </form>
</template>

<style scoped>
.form {
  display: flex;
  flex-direction: column;
  gap: 0;
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

.text-input,
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
}

.text-input:focus,
.textarea:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.45);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.textarea {
  resize: vertical;
  min-height: 88px;
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
