<script setup>
import LifeRpgDailyForm from './LifeRpgDailyForm.vue'

defineProps({
  profile: { type: Object, required: true },
  dailyForm: { type: Object, required: true },
  loading: { type: Boolean, default: false },
})

const emit = defineEmits(['submit-daily', 'edit-character', 'reset', 'update:dailyForm'])
</script>

<template>
  <div class="today-world">
    <section class="tool-card tool-card--soft character-brief">
      <p class="kicker">你的角色</p>
      <h2 class="character-name">{{ profile.routeTitle }}</h2>
      <p class="character-summary">{{ profile.routeSummary }}</p>
      <p v-if="profile.lifeKeywords?.length" class="character-kw">
        {{ profile.lifeKeywords.join(' · ') }}
      </p>
    </section>

    <section class="tool-card">
      <h2 class="block-title">同步今日状态</h2>
      <p class="sync-hint">不用填复杂表单，告诉 AI 今天的状态即可生成安排。</p>
      <LifeRpgDailyForm
        :model-value="dailyForm"
        :loading="loading"
        compact
        @update:model-value="emit('update:dailyForm', $event)"
        @submit="emit('submit-daily')"
      />
    </section>

    <div class="secondary-actions">
      <button type="button" class="btn-outline" @click="emit('edit-character')">调整人生角色</button>
      <button type="button" class="btn-outline btn-outline--danger" @click="emit('reset')">重置角色数据</button>
    </div>
  </div>
</template>

<style scoped>
.today-world {
  display: flex;
  flex-direction: column;
}

.character-name {
  margin: 0 0 8px;
  font-size: 20px;
  font-weight: 800;
  line-height: 1.35;
}

.character-summary,
.character-kw {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-muted);
}

.character-kw {
  margin-top: 8px;
  font-weight: 600;
  color: var(--accent-a);
}

.sync-hint {
  margin: 0 0 10px;
  font-size: 13px;
  color: var(--text-muted);
}

.secondary-actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 4px;
}
</style>
