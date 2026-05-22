<script setup>
import { computed } from 'vue'

const props = defineProps({
  attributes: { type: Object, required: true },
})

const rows = computed(() => [
  { key: 'energy', label: '精力值' },
  { key: 'explore', label: '探索值' },
  { key: 'express', label: '表达值' },
  { key: 'discipline', label: '自律值' },
  { key: 'social', label: '社交值' },
  { key: 'growth', label: '成长值' },
])

function barWidth(value) {
  const n = Math.min(100, Math.max(0, Number(value) || 0) * 8)
  return `${n}%`
}
</script>

<template>
  <section class="tool-card attr-panel">
    <h2 class="block-title">我的角色属性</h2>
    <div class="attr-grid">
      <div v-for="row in rows" :key="row.key" class="attr-row">
        <div class="attr-head">
          <span class="attr-label">{{ row.label }}</span>
          <span class="attr-value">{{ attributes[row.key] ?? 0 }}</span>
        </div>
        <div class="attr-bar" aria-hidden="true">
          <div class="attr-fill" :style="{ width: barWidth(attributes[row.key]) }" />
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.attr-grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.attr-head {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 6px;
}

.attr-label {
  font-size: 13px;
  font-weight: 600;
}

.attr-value {
  font-size: 14px;
  font-weight: 800;
  font-variant-numeric: tabular-nums;
}

.attr-bar {
  height: 6px;
  border-radius: 999px;
  overflow: hidden;
}

.attr-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.35s ease;
}
</style>
