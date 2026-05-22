<script setup>
const props = defineProps({
  choice: { type: Object, required: true },
  selected: { type: Boolean, default: false },
})

const emit = defineEmits(['select'])
</script>

<template>
  <button
    type="button"
    class="path-card"
    :class="{ 'path-card--selected': selected }"
    :aria-pressed="selected"
    @click="emit('select', choice.name)"
  >
    <span class="path-name">{{ choice.name }}</span>
    <span class="path-desc">{{ choice.description }}</span>
    <p class="path-suggestion">{{ choice.suggestion }}</p>
    <span v-if="selected" class="path-badge">今日已选</span>
  </button>
</template>

<style scoped>
.path-card {
  width: 100%;
  text-align: left;
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(255, 255, 255, 0.95);
  margin-bottom: 10px;
  cursor: pointer;
  transition:
    border-color var(--transition),
    box-shadow var(--transition),
    background var(--transition);
  font-family: inherit;
}

.path-card:hover {
  border-color: rgba(99, 102, 241, 0.4);
}

.path-card--selected {
  border-color: rgba(99, 102, 241, 0.55);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.08));
  box-shadow: 0 0 0 1px rgba(99, 102, 241, 0.15);
}

.path-name {
  display: block;
  font-size: 15px;
  font-weight: 700;
  color: #4338ca;
  margin-bottom: 4px;
}

.path-desc {
  display: block;
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 8px;
}

.path-suggestion {
  margin: 0;
  font-size: 14px;
  line-height: 1.55;
  color: var(--text);
}

.path-badge {
  display: inline-block;
  margin-top: 10px;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.15);
  color: #4338ca;
}
</style>
