<script setup>
import {
  BUDGET_OPTIONS,
  GOAL_OPTIONS,
  LIFE_STAGE_OPTIONS,
  PREFERENCE_OPTIONS,
  SOCIAL_STYLE_OPTIONS,
  WEEKEND_STATE_OPTIONS,
  WORK_STATE_OPTIONS,
} from '../../data/interestExplorerOptions.js'

const props = defineProps({
  modelValue: { type: Object, required: true },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'submit'])

function patch(partial) {
  emit('update:modelValue', { ...props.modelValue, ...partial })
}

function toggleMulti(field, label) {
  const list = [...(props.modelValue[field] || [])]
  const idx = list.indexOf(label)
  if (idx >= 0) list.splice(idx, 1)
  else list.push(label)
  patch({ [field]: list })
}

function isSelected(field, label) {
  return (props.modelValue[field] || []).includes(label)
}
</script>

<template>
  <form class="form" @submit.prevent="emit('submit')">
    <section class="card">
      <p class="field-label">当前阶段</p>
      <div class="chip-grid" role="radiogroup" aria-label="当前阶段">
        <button
          v-for="opt in LIFE_STAGE_OPTIONS"
          :key="opt"
          type="button"
          class="chip"
          :class="{ selected: modelValue.life_stage === opt }"
          role="radio"
          :aria-checked="modelValue.life_stage === opt"
          @click="patch({ life_stage: opt })"
        >
          {{ opt }}
        </button>
      </div>
    </section>

    <section class="card">
      <p class="field-label">工作/学习状态</p>
      <div class="chip-grid chip-grid--2" role="radiogroup" aria-label="工作学习状态">
        <button
          v-for="opt in WORK_STATE_OPTIONS"
          :key="opt"
          type="button"
          class="chip"
          :class="{ selected: modelValue.work_state === opt }"
          role="radio"
          :aria-checked="modelValue.work_state === opt"
          @click="patch({ work_state: opt })"
        >
          {{ opt }}
        </button>
      </div>
    </section>

    <section class="card">
      <p class="field-label">社交倾向</p>
      <div class="chip-grid chip-grid--2" role="radiogroup" aria-label="社交倾向">
        <button
          v-for="opt in SOCIAL_STYLE_OPTIONS"
          :key="opt"
          type="button"
          class="chip"
          :class="{ selected: modelValue.social_style === opt }"
          role="radio"
          :aria-checked="modelValue.social_style === opt"
          @click="patch({ social_style: opt })"
        >
          {{ opt }}
        </button>
      </div>
    </section>

    <section class="card">
      <p class="field-label">更喜欢 <span class="hint">可多选</span></p>
      <div class="chip-grid chip-grid--2" role="group" aria-label="更喜欢">
        <button
          v-for="opt in PREFERENCE_OPTIONS"
          :key="opt"
          type="button"
          class="chip chip--multi"
          :class="{ selected: isSelected('preferences', opt) }"
          :aria-pressed="isSelected('preferences', opt)"
          @click="toggleMulti('preferences', opt)"
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
      <p class="field-label">周末一般状态</p>
      <div class="chip-grid" role="radiogroup" aria-label="周末状态">
        <button
          v-for="opt in WEEKEND_STATE_OPTIONS"
          :key="opt"
          type="button"
          class="chip"
          :class="{ selected: modelValue.weekend_state === opt }"
          role="radio"
          :aria-checked="modelValue.weekend_state === opt"
          @click="patch({ weekend_state: opt })"
        >
          {{ opt }}
        </button>
      </div>
    </section>

    <section class="card">
      <p class="field-label">你最想获得什么 <span class="hint">可多选</span></p>
      <div class="chip-grid chip-grid--2" role="group" aria-label="最想获得什么">
        <button
          v-for="opt in GOAL_OPTIONS"
          :key="opt"
          type="button"
          class="chip chip--multi"
          :class="{ selected: isSelected('goals', opt) }"
          :aria-pressed="isSelected('goals', opt)"
          @click="toggleMulti('goals', opt)"
        >
          {{ opt }}
        </button>
      </div>
    </section>

    <section class="card">
      <label class="field-label" for="interest-extra">
        你最近的状态 / 想法 <span class="hint">可选</span>
      </label>
      <textarea
        id="interest-extra"
        class="textarea"
        rows="3"
        placeholder="例如：每天上班下班，不知道生活还有什么；想培养点长期爱好；想尝试运动但坚持不下去"
        :value="modelValue.extra_notes"
        @input="patch({ extra_notes: ($event.target).value })"
      />
    </section>

    <button type="submit" class="btn btn-gradient submit-btn" :disabled="loading">
      {{ loading ? 'AI 正在分析适合你的生活节奏...' : 'AI 帮我找兴趣' }}
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
  border-color: rgba(16, 185, 129, 0.45);
  box-shadow: 0 0 0 3px rgba(16, 185, 129, 0.12);
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
  border-color: rgba(16, 185, 129, 0.35);
}

.chip.selected {
  border-color: rgba(16, 185, 129, 0.55);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(52, 211, 153, 0.08));
  box-shadow: 0 0 0 1px rgba(16, 185, 129, 0.12);
  color: #047857;
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
  background: linear-gradient(135deg, #10b981 0%, #34d399 55%, #6ee7b7 100%) !important;
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.28) !important;
}
</style>
