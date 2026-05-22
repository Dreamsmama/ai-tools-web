<script setup>
defineProps({
  profile: { type: Object, required: true },
})

const emit = defineEmits(['enter-today', 'edit-character'])
</script>

<template>
  <section class="route-ready">
    <div class="tool-card tool-card--soft route-ready__card">
      <p class="kicker">第二阶段 · AI 人生路线已生成</p>
      <h2 class="route-ready__title">{{ profile.routeTitle }}</h2>
      <p class="route-ready__summary">{{ profile.routeSummary }}</p>
      <p v-if="profile.longTermMainLine" class="route-ready__line">{{ profile.longTermMainLine }}</p>
      <p v-if="profile.lifeKeywords?.length" class="route-ready__kw">
        核心关键词：{{ profile.lifeKeywords.join(' · ') }}
      </p>
    </div>

    <p class="route-ready__hint">角色与路线已就绪。接下来同步今天的状态，即可生成今日安排。</p>

    <button type="button" class="btn btn-gradient submit-btn" @click="emit('enter-today')">
      开始今天
    </button>
    <button type="button" class="btn-outline" @click="emit('edit-character')">调整人生角色</button>
  </section>
</template>

<style scoped>
.route-ready {
  display: flex;
  flex-direction: column;
}

.route-ready__title {
  margin: 0 0 10px;
  font-size: 20px;
  font-weight: 800;
  line-height: 1.35;
}

.route-ready__summary,
.route-ready__line,
.route-ready__kw {
  margin: 0 0 8px;
  font-size: 14px;
  line-height: 1.65;
  color: var(--text-muted);
}

.route-ready__hint {
  margin: 0 0 14px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-muted);
}
</style>
