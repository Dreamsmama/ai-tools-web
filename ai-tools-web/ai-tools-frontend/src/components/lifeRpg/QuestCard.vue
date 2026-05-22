<script setup>
defineProps({
  title: { type: String, default: '' },
  goal: { type: String, default: '' },
  estimatedTime: { type: String, default: '' },
})
</script>

<template>
  <article class="quest">
    <h3 v-if="title" class="quest-title">{{ title }}</h3>
    <p v-if="goal" class="quest-goal">{{ goal }}</p>
    <p v-if="estimatedTime" class="quest-meta">预计总耗时：{{ estimatedTime }}</p>
  </article>
</template>
