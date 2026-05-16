<script setup>
import { RouterLink } from 'vue-router'
import { gaokaoHotTopics } from '../data/gaokao/hotTopics.js'
import { trackEvent } from '../analytics.js'

const hotPreview = gaokaoHotTopics.slice(0, 2)

function onTestClick() {
  trackEvent('gaokao_zone_test_click', {
    feature: 'gaokao',
    page: '/',
    props: { target: '/gaokao/test' },
  })
}

function onZoneClick() {
  trackEvent('gaokao_zone_enter', {
    feature: 'gaokao',
    page: '/',
    props: { target: '/gaokao' },
  })
}
</script>

<template>
  <section class="gaokao-section" aria-labelledby="gaokao-section-title">
    <div class="gaokao-glow" aria-hidden="true" />

    <div class="gaokao-head">
      <p class="gaokao-kicker">🎓 高考生专区</p>
      <h2 id="gaokao-section-title" class="gaokao-title">高考后不知道选什么专业？</h2>
      <p class="gaokao-sub">AI 帮你分析适合的发展方向：专业、职业与 AI 时代风险，不是分数线工具。</p>
    </div>

    <div class="gaokao-actions">
      <RouterLink class="gaokao-btn btn-gradient" to="/gaokao/test" @click="onTestClick">
        开始专业测试
      </RouterLink>
      <RouterLink class="gaokao-btn-secondary" to="/gaokao" @click="onZoneClick">
        进入高考生专区
      </RouterLink>
    </div>

    <ul class="hot-preview" role="list">
      <li v-for="topic in hotPreview" :key="topic.id" class="hot-preview-li">
        <RouterLink class="hot-preview-card" :to="`/gaokao/topics/${topic.slug}`" @click="onZoneClick">
          <span class="hot-tag" :class="`hot-tag--${topic.tone}`">{{ topic.tag }}</span>
          <span class="hot-title">{{ topic.title }}</span>
        </RouterLink>
      </li>
    </ul>
  </section>
</template>

<style scoped>
.gaokao-section {
  position: relative;
  overflow: hidden;
  margin: 0 12px 20px;
  padding: 22px 18px 18px;
  border-radius: calc(var(--radius) + 2px);
  background: linear-gradient(
    145deg,
    rgba(224, 242, 254, 0.95) 0%,
    rgba(237, 233, 254, 0.92) 48%,
    rgba(255, 255, 255, 0.96) 100%
  );
  border: 1px solid rgba(99, 102, 241, 0.22);
  box-shadow: var(--shadow-card);
}

.gaokao-glow {
  position: absolute;
  top: -40%;
  right: -20%;
  width: 60%;
  height: 80%;
  background: radial-gradient(circle, rgba(6, 182, 212, 0.2), transparent 70%);
  pointer-events: none;
}

.gaokao-head {
  position: relative;
}

.gaokao-kicker {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: #0891b2;
}

.gaokao-title {
  margin: 0 0 8px;
  font-size: 18px;
  font-weight: 800;
  line-height: 1.35;
  color: var(--text);
}

.gaokao-sub {
  margin: 0;
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-muted);
}

.gaokao-actions {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 16px 0 14px;
}

@media (min-width: 420px) {
  .gaokao-actions {
    flex-direction: row;
    flex-wrap: wrap;
  }
}

.gaokao-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12px 18px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  text-decoration: none;
  color: #fff;
  flex: 1;
  min-width: 140px;
}

.gaokao-btn-secondary {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 12px 18px;
  border-radius: 14px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  color: #5b21b6;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(99, 102, 241, 0.28);
  flex: 1;
  min-width: 140px;
}

.hot-preview {
  position: relative;
  list-style: none;
  margin: 0;
  padding: 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}

.hot-preview-card {
  display: flex;
  flex-direction: column;
  gap: 6px;
  padding: 10px 12px;
  border-radius: 12px;
  text-decoration: none;
  background: rgba(255, 255, 255, 0.75);
  border: 1px solid rgba(148, 163, 184, 0.25);
  transition: transform var(--transition);
}

.hot-preview-card:hover {
  transform: translateY(-2px);
}

.hot-tag {
  align-self: flex-start;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
}

.hot-tag--alert {
  color: #b91c1c;
  background: rgba(254, 226, 226, 0.9);
}

.hot-tag--insight {
  color: #5b21b6;
  background: rgba(237, 233, 254, 0.95);
}

.hot-tag--guide {
  color: #0f766e;
  background: rgba(204, 251, 241, 0.9);
}

.hot-title {
  font-size: 12px;
  font-weight: 700;
  line-height: 1.4;
  color: var(--text);
}
</style>
