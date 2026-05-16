<script setup>
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { gaokaoHotTopics } from '../data/gaokao/hotTopics.js'
import { majorFutureExperiences } from '../data/gaokao/majorExperiences.js'
import { trackEvent } from '../analytics.js'

const PAGE = '/gaokao'
const FEATURE = 'gaokao'

onMounted(() => {
  trackEvent('gaokao_zone_view', { feature: FEATURE, page: PAGE })
})

function onTestClick() {
  trackEvent('gaokao_zone_test_click', { feature: FEATURE, page: PAGE, props: { target: '/gaokao/test' } })
}

function onTopicClick(slug) {
  trackEvent('gaokao_hot_topic_click', { feature: FEATURE, page: PAGE, props: { slug } })
}

function onExperienceClick(id) {
  trackEvent('gaokao_major_experience_click', { feature: FEATURE, page: PAGE, props: { experience_id: id } })
}
</script>

<template>
  <div class="page">
    <RouterLink class="back" to="/">← 返回首页</RouterLink>

    <header class="hero">
      <p class="kicker">🎓 高考生专区</p>
      <h1 class="h1">选专业，也是在选未来的自己</h1>
      <p class="sub">
        不做分数线与院校推荐。我们帮你从职业倾向出发，看见适合的专业方向、对应职业与 AI 时代风险。
      </p>
      <RouterLink class="btn-main btn-gradient" to="/gaokao/test" @click="onTestClick">
        开始专业测试
      </RouterLink>
      <p class="hero-note">约 3 分钟 · 复用职业倾向题库 · 本地规则生成结果</p>
    </header>

    <section class="block" aria-labelledby="hot-title">
      <h2 id="hot-title" class="block-title">高考热点</h2>
      <p class="block-sub">选专业前先看趋势与风险，每篇约 4 分钟。</p>
      <ul class="topic-grid" role="list">
        <li v-for="topic in gaokaoHotTopics" :key="topic.id" class="topic-li">
          <RouterLink
            class="topic-card topic-card--link"
            :class="`topic-card--${topic.tone}`"
            :to="`/gaokao/topics/${topic.slug}`"
            @click="onTopicClick(topic.slug)"
          >
            <span class="topic-tag">{{ topic.tag }}</span>
            <h3 class="topic-title">{{ topic.title }}</h3>
            <p class="topic-teaser">{{ topic.teaser }}</p>
            <span class="topic-cta">阅读解读 ›</span>
          </RouterLink>
        </li>
      </ul>
    </section>

    <section class="block" aria-labelledby="exp-title">
      <h2 id="exp-title" class="block-title">专业 → 未来职业体验</h2>
      <p class="block-sub">像人生模拟一样，感受「学这个专业以后」真实又荒诞的一天。</p>
      <ul class="exp-list" role="list">
        <li v-for="item in majorFutureExperiences" :key="item.id" class="exp-li">
          <RouterLink
            v-if="item.available"
            class="exp-card exp-card--on"
            :to="item.to"
            @click="onExperienceClick(item.id)"
          >
            <span class="exp-emoji" aria-hidden="true">{{ item.posterEmoji }}</span>
            <div class="exp-body">
              <p class="exp-major">{{ item.majorLabel }}</p>
              <p class="exp-title">{{ item.title }}</p>
              <p class="exp-tagline">{{ item.tagline }}</p>
              <span class="exp-cta">进入体验 ›</span>
            </div>
          </RouterLink>
          <div v-else class="exp-card exp-card--off" aria-disabled="true">
            <span class="exp-emoji" aria-hidden="true">{{ item.posterEmoji }}</span>
            <div class="exp-body">
              <p class="exp-major">{{ item.majorLabel }}</p>
              <p class="exp-title">{{ item.title }}</p>
              <p class="exp-tagline">{{ item.tagline }}</p>
              <span class="exp-badge">开发中</span>
            </div>
          </div>
        </li>
      </ul>
      <RouterLink class="link-more" to="/career-experience">前往 AI 职业体验馆 ›</RouterLink>
    </section>
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
  color: #0891b2;
}

.hero {
  margin: 0 4px 24px;
  padding: 22px 18px;
  border-radius: var(--radius);
  background: linear-gradient(145deg, #ecfeff 0%, #ede9fe 55%, #fff 100%);
  border: 1px solid rgba(6, 182, 212, 0.25);
  box-shadow: var(--shadow-card);
}

.kicker {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 700;
  color: #0891b2;
}

.h1 {
  margin: 0 0 10px;
  font-size: 24px;
  font-weight: 800;
  line-height: 1.3;
  color: var(--text);
}

.sub {
  margin: 0 0 18px;
  font-size: 14px;
  line-height: 1.65;
  color: var(--text-muted);
}

.btn-main {
  display: inline-flex;
  padding: 13px 22px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  text-decoration: none;
  color: #fff;
}

.hero-note {
  margin: 12px 0 0;
  font-size: 12px;
  color: var(--text-muted);
}

.block {
  margin: 0 4px 28px;
}

.block-title {
  margin: 0 0 6px;
  font-size: 18px;
  font-weight: 800;
  color: var(--text);
}

.block-sub {
  margin: 0 0 14px;
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.5;
}

.topic-grid {
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  gap: 12px;
}

@media (min-width: 520px) {
  .topic-grid {
    grid-template-columns: 1fr 1fr;
  }
}

.topic-card {
  display: block;
  padding: 16px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.28);
  background: var(--surface-solid);
  box-shadow: var(--shadow-card);
  text-decoration: none;
  color: inherit;
  transition: transform var(--transition);
}

.topic-card--link:hover {
  transform: translateY(-2px);
}

.topic-card--alert {
  border-color: rgba(248, 113, 113, 0.35);
}

.topic-card--insight {
  border-color: rgba(99, 102, 241, 0.3);
}

.topic-card--guide {
  border-color: rgba(20, 184, 166, 0.35);
}

.topic-tag {
  display: inline-block;
  margin-bottom: 8px;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  color: #5b21b6;
  background: rgba(99, 102, 241, 0.1);
}

.topic-title {
  margin: 0 0 8px;
  font-size: 16px;
  font-weight: 800;
  color: var(--text);
  line-height: 1.35;
}

.topic-teaser {
  margin: 0 0 12px;
  font-size: 13px;
  line-height: 1.55;
  color: var(--text-muted);
}

.topic-cta {
  display: inline-block;
  margin-top: 4px;
  font-size: 13px;
  font-weight: 600;
  color: #0891b2;
}

.exp-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.exp-li + .exp-li {
  margin-top: 10px;
}

.exp-card {
  display: flex;
  gap: 14px;
  padding: 16px;
  border-radius: 14px;
  border: var(--border-soft);
  text-decoration: none;
  color: inherit;
}

.exp-card--on {
  background: linear-gradient(135deg, rgba(238, 242, 255, 0.95), rgba(255, 255, 255, 0.98));
  box-shadow: var(--shadow-card);
  transition: transform var(--transition);
}

.exp-card--on:hover {
  transform: translateY(-2px);
}

.exp-card--off {
  background: rgba(248, 250, 252, 0.8);
  opacity: 0.55;
  cursor: not-allowed;
}

.exp-emoji {
  font-size: 32px;
  line-height: 1;
}

.exp-major {
  margin: 0 0 4px;
  font-size: 11px;
  font-weight: 700;
  color: #6366f1;
}

.exp-title {
  margin: 0 0 6px;
  font-size: 16px;
  font-weight: 800;
  color: var(--text);
}

.exp-tagline {
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-muted);
}

.exp-cta {
  display: inline-block;
  margin-top: 10px;
  font-size: 13px;
  font-weight: 600;
  color: #5b21b6;
}

.exp-badge {
  display: inline-block;
  margin-top: 10px;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  color: var(--text-muted);
  background: rgba(148, 163, 184, 0.15);
}

.link-more {
  display: inline-block;
  margin-top: 14px;
  font-size: 13px;
  font-weight: 600;
  color: #0891b2;
  text-decoration: none;
}
</style>
