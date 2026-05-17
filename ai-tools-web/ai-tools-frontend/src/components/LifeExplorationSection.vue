<script setup>
import { RouterLink } from 'vue-router'
import { trackEvent } from '../analytics.js'

function onInterestClick() {
  trackEvent('home_life_interest_click', {
    feature: 'interest_explorer',
    page: '/',
    props: { target: '/tools/interest-explorer' },
  })
}

function onEveningClick() {
  trackEvent('home_life_evening_click', {
    feature: 'evening_plan',
    page: '/',
    props: { target: '/tools/evening-plan' },
  })
}
</script>

<template>
  <section class="life-section" aria-labelledby="life-section-title">
    <header class="life-head">
      <p class="life-kicker">兴趣与生活</p>
      <h2 id="life-section-title" class="life-title">不只工作，也帮你找到下班后的生活方向</h2>
      <p class="life-sub">
        分析你的生活节奏、性格和偏好，推荐真正适合长期坚持的兴趣、运动、吃喝玩乐和成长方式。
      </p>
    </header>

    <div class="life-grid">
      <RouterLink
        class="life-card life-card--interest"
        to="/tools/interest-explorer"
        @click="onInterestClick"
      >
        <div class="life-card-accent" aria-hidden="true" />
        <span class="life-card-tag life-card-tag--mint">兴趣</span>
        <h3 class="life-card-title">AI 兴趣推荐 / 兴趣探索器</h3>
        <p class="life-card-desc">找到适合长期坚持的爱好</p>
        <span class="life-card-cta life-card-cta--mint">AI 帮我找兴趣</span>
      </RouterLink>

      <RouterLink
        class="life-card life-card--evening"
        to="/tools/evening-plan"
        @click="onEveningClick"
      >
        <div class="life-card-accent" aria-hidden="true" />
        <span class="life-card-tag life-card-tag--warm">生活</span>
        <h3 class="life-card-title">下班后不知道干什么</h3>
        <p class="life-card-desc">测测你今晚适合吃什么、去哪玩、做什么</p>
        <span class="life-card-cta">AI 帮我安排今晚</span>
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.life-section {
  margin: 0 12px 28px;
}

.life-head {
  margin-bottom: 16px;
  padding: 0 4px;
}

.life-kicker {
  margin: 0 0 8px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #6366f1;
}

.life-title {
  margin: 0 0 10px;
  font-size: 20px;
  font-weight: 800;
  line-height: 1.35;
  letter-spacing: -0.02em;
  color: var(--text);
}

.life-sub {
  margin: 0;
  font-size: 14px;
  line-height: 1.65;
  color: var(--text-muted);
}

.life-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 12px;
}

@media (min-width: 640px) {
  .life-grid {
    grid-template-columns: 1fr 1fr;
    gap: 14px;
  }
}

.life-card {
  position: relative;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  padding: 20px 20px 18px 24px;
  border-radius: var(--radius);
  text-decoration: none;
  color: inherit;
  background: var(--surface-solid);
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
  transition:
    transform var(--transition),
    box-shadow var(--transition);
}

.life-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-float);
}

.life-card-accent {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  border-radius: 4px 0 0 4px;
}

.life-card--interest .life-card-accent {
  background: linear-gradient(180deg, #10b981, #34d399, #6ee7b7);
}

.life-card--evening .life-card-accent {
  background: linear-gradient(180deg, #f59e0b, #f97316, #fb7185);
}

.life-card-tag {
  align-self: flex-start;
  margin-bottom: 10px;
  font-size: 11px;
  font-weight: 600;
  padding: 5px 11px;
  border-radius: 999px;
}

.life-card-tag--mint {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(52, 211, 153, 0.12));
  color: #047857;
  border: 1px solid rgba(16, 185, 129, 0.28);
}

.life-card-tag--warm {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(251, 113, 133, 0.12));
  color: #c2410c;
  border: 1px solid rgba(245, 158, 11, 0.28);
}

.life-card-title {
  margin: 0 0 8px;
  font-size: 17px;
  font-weight: 700;
  color: var(--text);
  line-height: 1.35;
}

.life-card-desc {
  margin: 0;
  flex: 1;
  font-size: 14px;
  line-height: 1.55;
  color: var(--text-muted);
}

.life-card-cta {
  display: inline-block;
  margin-top: 16px;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  border-radius: 999px;
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 55%, #fb7185 100%);
  box-shadow: 0 6px 18px rgba(249, 115, 22, 0.28);
}

.life-card-cta--mint {
  background: linear-gradient(135deg, #10b981 0%, #34d399 55%, #6ee7b7 100%);
  box-shadow: 0 6px 18px rgba(16, 185, 129, 0.28);
}
</style>
