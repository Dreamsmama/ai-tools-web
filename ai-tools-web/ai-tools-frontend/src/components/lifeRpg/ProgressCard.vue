<script setup>
import { computed } from 'vue'
import { getProgressFeedback } from '../../lib/lifeRpgProgress.js'

const props = defineProps({
  completed: { type: Number, default: 0 },
  total: { type: Number, default: 0 },
})

const progress = computed(() => getProgressFeedback(props.completed, props.total))
</script>

<template>
  <section class="tool-card">
    <h2 class="block-title">今日推进进度</h2>
    <div class="progress-bar" aria-hidden="true">
      <div class="progress-fill" :style="{ width: `${progress.percent}%` }" />
    </div>
    <p class="progress-stats">
      已完成 <strong>{{ progress.completed }}</strong> / {{ progress.total }}
      <span class="percent">（{{ progress.percent }}%）</span>
    </p>
    <p class="progress-text">{{ progress.text }}</p>
  </section>
</template>

<style scoped>
.progress-bar {
  height: 8px;
  border-radius: 999px;
  overflow: hidden;
  margin-bottom: 10px;
}

.progress-stats {
  margin: 0 0 6px;
  font-size: 14px;
}

.percent {
  color: var(--text-muted);
  font-size: 13px;
}

.progress-text {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--accent-a);
  line-height: 1.5;
}
</style>
