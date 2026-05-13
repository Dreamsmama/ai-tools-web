<script setup>
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { listCareerExperienceHubItems } from '../data/careerExperience/index.js'
import { trackEvent } from '../analytics.js'

const PAGE = '/career-experience'
const FEATURE = 'career_experience'

const items = listCareerExperienceHubItems()

onMounted(() => {
  trackEvent('career_experience_hub_view', { feature: FEATURE, page: PAGE })
})
</script>

<template>
  <div class="page">
    <RouterLink class="back" to="/">← 返回首页</RouterLink>

    <header class="head">
      <p class="kicker">互动体验</p>
      <h1 class="h1">AI 职业体验馆</h1>
      <p class="sub">像打开工作 IM 一样，体验一个职业真实的一天</p>
    </header>

    <p class="hint">这不是职业测试。你只是在一天里不断收到消息，然后在没有完美答案的情况下做选择。</p>

    <ul class="list" role="list">
      <li v-for="item in items" :key="item.id" class="li">
        <RouterLink
          v-if="item.available"
          class="card card--on"
          :to="item.to"
          @click="
            trackEvent('career_experience_pick', {
              feature: FEATURE,
              page: PAGE,
              props: { experience_id: item.id },
            })
          "
        >
          <span class="card-title">{{ item.title }}</span>
          <span class="badge badge--live">{{ item.subtitle }}</span>
          <span class="chev" aria-hidden="true">›</span>
        </RouterLink>
        <div v-else class="card card--off" aria-disabled="true">
          <span class="card-title">{{ item.title }}</span>
          <span class="badge badge--soon">{{ item.subtitle }}</span>
        </div>
      </li>
    </ul>

    <p class="foot-note">更多职业剧情陆续开放中。</p>
  </div>
</template>

<style scoped>
.page {
  max-width: 720px;
  margin: 0 auto;
  padding: 24px 16px 48px;
  min-height: 100vh;
}

.back {
  display: inline-block;
  margin: 0 4px 20px;
  font-size: 14px;
  color: var(--text-muted);
  text-decoration: none;
}

.back:hover {
  color: var(--accent-a);
}

.head {
  margin: 0 4px 16px;
}

.kicker {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #5b21b6;
}

.h1 {
  margin: 0;
  font-size: 26px;
  font-weight: 800;
  letter-spacing: -0.02em;
  line-height: 1.2;
}

.sub {
  margin: 10px 0 0;
  font-size: 15px;
  color: var(--text-muted);
  line-height: 1.5;
}

.hint {
  margin: 0 4px 20px;
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.2);
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.55;
}

.list {
  list-style: none;
  margin: 0;
  padding: 0 4px;
}

.li + .li {
  margin-top: 12px;
}

.card {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 18px 18px 18px 20px;
  border-radius: var(--radius);
  border: var(--border-soft);
  background: var(--surface-solid);
  box-shadow: var(--shadow-card);
  text-decoration: none;
  color: inherit;
  position: relative;
  overflow: hidden;
  transition:
    transform var(--transition),
    box-shadow var(--transition);
}

.card--on::before {
  content: '';
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, #6366f1, #a855f7);
  border-radius: 4px 0 0 4px;
}

.card--on:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-float);
}

.card--off {
  opacity: 0.55;
  cursor: not-allowed;
  filter: grayscale(0.15);
}

.card-title {
  flex: 1;
  font-size: 17px;
  font-weight: 700;
}

.badge {
  font-size: 11px;
  font-weight: 700;
  padding: 5px 10px;
  border-radius: 999px;
  border: 1px solid transparent;
}

.badge--live {
  color: #5b21b6;
  background: rgba(99, 102, 241, 0.12);
  border-color: rgba(99, 102, 241, 0.25);
}

.badge--soon {
  color: var(--text-muted);
  background: rgba(148, 163, 184, 0.15);
  border-color: rgba(148, 163, 184, 0.35);
}

.chev {
  font-size: 22px;
  font-weight: 300;
  color: var(--text-muted);
  line-height: 1;
}

.foot-note {
  margin: 24px 4px 0;
  font-size: 12px;
  color: var(--text-muted);
}
</style>
