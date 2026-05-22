<script setup>
const props = defineProps({
  task: { type: Object, required: true },
  completed: { type: Boolean, default: false },
  variant: { type: String, default: 'main' },
})

const emit = defineEmits(['toggle'])

const rewardLabels = [
  { key: 'energy', label: '精力' },
  { key: 'explore', label: '探索' },
  { key: 'express', label: '表达' },
  { key: 'discipline', label: '自律' },
  { key: 'social', label: '社交' },
  { key: 'growth', label: '成长' },
]

function rewardParts(reward) {
  if (!reward) return []
  return rewardLabels
    .map(({ key, label }) => ({ label, val: Number(reward[key]) || 0 }))
    .filter((r) => r.val > 0)
    .map((r) => `${r.label}+${r.val}`)
}
</script>

<template>
  <article class="task-item" :class="{ 'task-item--done': completed }">
    <div class="task-head">
      <h4 class="task-title">{{ task.title }}</h4>
      <span v-if="completed" class="done-badge">已完成</span>
    </div>
    <p class="task-action">{{ task.action }}</p>
    <p v-if="task.estimated_time" class="task-meta">预计耗时：{{ task.estimated_time }}</p>
    <p v-if="rewardParts(task.reward).length" class="task-reward">
      完成奖励：{{ rewardParts(task.reward).join(' · ') }}
    </p>
    <p v-if="task.reward_text" class="task-reward-text">{{ task.reward_text }}</p>
    <button
      type="button"
      class="task-btn"
      :class="{ 'task-btn--outline': completed }"
      @click="emit('toggle')"
    >
      {{ completed ? '取消完成' : '标记完成' }}
    </button>
  </article>
</template>

<style scoped>
.task-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
  margin-bottom: 6px;
}

.done-badge {
  flex-shrink: 0;
  font-size: 10px;
  font-weight: 700;
  padding: 3px 8px;
  border-radius: 999px;
  background: rgba(34, 197, 94, 0.15);
  color: #15803d;
}

.task-meta,
.task-reward {
  margin: 0 0 6px;
  font-size: 13px;
  font-weight: 600;
}

.task-reward-text {
  margin: 0 0 10px;
  font-size: 13px;
  color: var(--text-muted);
}

.task-item:last-child {
  margin-bottom: 0;
}
</style>
