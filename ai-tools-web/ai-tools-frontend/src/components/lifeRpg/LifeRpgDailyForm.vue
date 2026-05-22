<script setup>
import { DAILY_MODE_OPTIONS, ENERGY_OPTIONS, GO_OUT_OPTIONS } from '../../data/lifeRpgOptions.js'

const props = defineProps({
  modelValue: { type: Object, required: true },
  loading: { type: Boolean, default: false },
  compact: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'submit'])

function patch(partial) {
  emit('update:modelValue', { ...props.modelValue, ...partial })
}
</script>

<template>
  <form class="form" :class="{ 'form--compact': compact }" @submit.prevent="emit('submit')">
    <section :class="compact ? 'section' : 'tool-card'">
      <p class="field-label">今天的精力状态</p>
      <div class="chip-grid" role="radiogroup">
        <button
          v-for="opt in ENERGY_OPTIONS"
          :key="opt"
          type="button"
          class="chip"
          :class="{ selected: modelValue.energy_level === opt }"
          @click="patch({ energy_level: opt })"
        >
          {{ opt }}
        </button>
      </div>
    </section>

    <section :class="compact ? 'section' : 'tool-card'">
      <p class="field-label">今天想怎么推进</p>
      <div class="chip-grid chip-grid--2" role="radiogroup">
        <button
          v-for="opt in DAILY_MODE_OPTIONS"
          :key="opt"
          type="button"
          class="chip"
          :class="{ selected: modelValue.daily_mode === opt }"
          @click="patch({ daily_mode: opt })"
        >
          {{ opt }}
        </button>
      </div>
    </section>

    <section :class="compact ? 'section' : 'tool-card'">
      <p class="field-label">今天是否想出门</p>
      <div class="chip-grid" role="radiogroup">
        <button
          v-for="opt in GO_OUT_OPTIONS"
          :key="opt"
          type="button"
          class="chip"
          :class="{ selected: modelValue.go_out === opt }"
          @click="patch({ go_out: opt })"
        >
          {{ opt }}
        </button>
      </div>
    </section>

    <section :class="compact ? 'section' : 'tool-card'">
      <label class="field-label" for="life-rpg-custom-tasks">今天想多做的一件事 <span class="hint">可选</span></label>
      <textarea
        id="life-rpg-custom-tasks"
        class="textarea"
        rows="3"
        placeholder="例如：今天想练吉他 20 分钟；今天只想休息一下"
        :value="modelValue.custom_tasks"
        @input="patch({ custom_tasks: ($event.target).value })"
      />
    </section>

    <button type="submit" class="btn btn-gradient submit-btn" :disabled="loading">
      {{ loading ? 'AI 正在生成你今天的安排…' : '生成今日安排' }}
    </button>
  </form>
</template>

<style scoped>
.form--compact .section {
  margin-bottom: 12px;
}

.form--compact .section:last-of-type {
  margin-bottom: 0;
}
</style>
