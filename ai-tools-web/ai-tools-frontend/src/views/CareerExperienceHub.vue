<script setup>
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { listCareerExperienceHubItems } from '../data/careerExperience/index.js'
import { trackEvent } from '../analytics.js'

const PAGE = '/career-experience'
const FEATURE = 'career_experience'

const items = listCareerExperienceHubItems()

onMounted(() => {
  trackEvent('career_experience_hub_view', {
    feature: FEATURE,
    page: PAGE,
    props: { hub: 'career_experience' },
  })
})
</script>

<template>
  <div class="page">
    <RouterLink class="back" to="/">← 返回首页</RouterLink>

    <header class="head">
      <p class="kicker">互动体验</p>
      <h1 class="h1">AI 职业体验馆</h1>
      <p class="sub">体验「已经上班以后」真实又荒诞的一天——职场人视角，不是校园视角。</p>
    </header>

    <p class="hint">这不是职业测试。你只是在工作消息里，选一个没那么崩的。</p>

    <RouterLink class="gaokao-banner" to="/gaokao">
      <span class="gaokao-banner-kicker">🎓 高考生专区</span>
      <span class="gaokao-banner-title">想体验「学这个专业以后」？</span>
      <span class="gaokao-banner-sub">法学 / 金融 / 医学等专业在读视角，与下方职场体验不同 ›</span>
    </RouterLink>

    <h2 class="section-h2">职场一日体验</h2>
    <p class="section-sub">程序员、律师、医生、金融从业者……已执业或在职的某一天。</p>
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
              props: { experience_id: item.id, hub: 'career_workplace' },
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
  margin: 0 4px 16px;
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.2);
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.55;
}

.gaokao-banner {
  display: flex;
  flex-direction: column;
  gap: 4px;
  margin: 0 4px 20px;
  padding: 14px 16px;
  border-radius: 14px;
  text-decoration: none;
  color: inherit;
  background: linear-gradient(135deg, rgba(224, 242, 254, 0.9), rgba(237, 233, 254, 0.85));
  border: 1px solid rgba(6, 182, 212, 0.3);
  transition: transform var(--transition);
}

.gaokao-banner:hover {
  transform: translateY(-2px);
}

.gaokao-banner-kicker {
  font-size: 11px;
  font-weight: 700;
  color: #0891b2;
}

.gaokao-banner-title {
  font-size: 15px;
  font-weight: 800;
  color: var(--text);
}

.gaokao-banner-sub {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.45;
}

.section-h2 {
  margin: 0 4px 6px;
  font-size: 16px;
  font-weight: 800;
  color: var(--text);
}

.section-sub {
  margin: 0 4px 12px;
  font-size: 13px;
  color: var(--text-muted);
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
