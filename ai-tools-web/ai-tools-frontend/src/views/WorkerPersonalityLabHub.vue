<script setup>
import { onMounted } from 'vue'
import { RouterLink } from 'vue-router'
import { WORKER_LAB_SERIES } from '../data/careerExperience/workerLabSeries.js'
import { trackEvent } from '../analytics.js'

const PAGE = '/worker-lab'
const FEATURE = 'career_experience'

const seriesList = WORKER_LAB_SERIES

onMounted(() => {
  trackEvent('career_experience_hub_view', {
    feature: FEATURE,
    page: PAGE,
    props: { hub: 'worker_lab', layout: 'series' },
  })
})

function onEpisodePick(seriesId, episode) {
  trackEvent('career_experience_pick', {
    feature: FEATURE,
    page: PAGE,
    props: {
      series_id: seriesId,
      episode_id: episode.id,
      experience_key: episode.experienceKey,
      hub: 'worker_lab',
    },
  })
}
</script>

<template>
  <div class="page">
    <RouterLink class="back" to="/">← 返回首页</RouterLink>

    <header class="head">
      <p class="kicker">🎭 打工人格实验室</p>
      <h1 class="h1">互动职场连续剧</h1>
      <p class="sub">按系列追剧，一集一集看打工人的一天怎么失控。</p>
    </header>

    <p class="hint">这里没有标准答案。你只是在不断弹出的消息里，选一个没那么崩的。</p>

    <div v-for="series in seriesList" :key="series.id" class="series-block">
      <header class="series-head">
        <span class="series-emoji" aria-hidden="true">{{ series.posterEmoji }}</span>
        <div>
          <h2 class="series-title">{{ series.title }}</h2>
          <p class="series-tagline">{{ series.tagline }}</p>
        </div>
      </header>

      <ul class="ep-list" role="list">
        <li v-for="ep in series.episodes" :key="ep.id" class="ep-li">
          <RouterLink
            v-if="ep.status === 'open'"
            class="ep-card ep-card--open"
            :to="ep.to"
            @click="onEpisodePick(series.id, ep)"
          >
            <div class="ep-poster" :class="`ep-poster--${series.posterClass}`" aria-hidden="true">
              <span class="ep-code">{{ ep.code }}</span>
              <span class="ep-emoji">{{ ep.posterEmoji }}</span>
            </div>
            <div class="ep-main">
              <p class="ep-meta">{{ ep.code }} · {{ ep.title }}</p>
              <p class="ep-tagline">{{ ep.tagline }}</p>
              <span class="ep-cta">开始追剧 ›</span>
            </div>
          </RouterLink>

          <div v-else class="ep-card ep-card--locked" aria-disabled="true">
            <div class="ep-poster ep-poster--locked" aria-hidden="true">
              <span class="ep-code">{{ ep.code }}</span>
              <span class="ep-emoji">{{ ep.posterEmoji }}</span>
            </div>
            <div class="ep-main">
              <p class="ep-meta">{{ ep.code }} · {{ ep.title }}</p>
              <p class="ep-tagline">{{ ep.tagline }}</p>
              <span class="ep-badge">开发中</span>
            </div>
          </div>
        </li>
      </ul>
    </div>

    <p class="foot-note">同一系列会陆续更新新集，不用换职业也能继续追。</p>
  </div>
</template>

<style scoped>
.page {
  max-width: 720px;
  margin: 0 auto;
  padding: 24px 16px 48px;
  min-height: 100vh;
  background: linear-gradient(180deg, #0f172a 0%, #1e1b4b 35%, #0f172a 100%);
}

.back {
  display: inline-block;
  margin: 0 4px 20px;
  font-size: 14px;
  color: rgba(203, 213, 225, 0.75);
  text-decoration: none;
}

.back:hover {
  color: #fda4af;
}

.head {
  margin: 0 4px 16px;
}

.kicker {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: #fda4af;
}

.h1 {
  margin: 0;
  font-size: 26px;
  font-weight: 800;
  letter-spacing: -0.02em;
  line-height: 1.2;
  color: #f8fafc;
}

.sub {
  margin: 10px 0 0;
  font-size: 15px;
  color: rgba(226, 232, 240, 0.78);
  line-height: 1.5;
}

.hint {
  margin: 0 4px 24px;
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  background: rgba(15, 23, 42, 0.55);
  border: 1px solid rgba(148, 163, 184, 0.25);
  font-size: 13px;
  color: rgba(203, 213, 225, 0.85);
  line-height: 1.55;
}

.series-block + .series-block {
  margin-top: 28px;
}

.series-head {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin: 0 4px 14px;
}

.series-emoji {
  font-size: 28px;
  line-height: 1;
}

.series-title {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: #f8fafc;
}

.series-tagline {
  margin: 6px 0 0;
  font-size: 13px;
  color: rgba(203, 213, 225, 0.78);
  line-height: 1.5;
}

.ep-list {
  list-style: none;
  margin: 0;
  padding: 0 4px;
}

.ep-li + .ep-li {
  margin-top: 10px;
}

.ep-card {
  display: flex;
  gap: 14px;
  padding: 14px 16px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.28);
  text-decoration: none;
  color: inherit;
}

.ep-card--open {
  background: rgba(15, 23, 42, 0.65);
  transition:
    transform var(--transition),
    border-color var(--transition),
    box-shadow var(--transition);
}

.ep-card--open:hover {
  transform: translateY(-2px);
  border-color: rgba(251, 113, 133, 0.45);
  box-shadow: 0 14px 28px rgba(0, 0, 0, 0.32);
}

.ep-card--locked {
  background: rgba(15, 23, 42, 0.35);
  border-color: rgba(100, 116, 139, 0.2);
  opacity: 0.55;
  cursor: not-allowed;
}

.ep-poster {
  flex-shrink: 0;
  width: 72px;
  min-height: 88px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  border: 1px solid rgba(148, 163, 184, 0.25);
}

.ep-poster--developer {
  background: linear-gradient(160deg, #1e3a5f, #0f172a);
}

.ep-poster--hr {
  background: linear-gradient(160deg, #4c1d95, #1e1b4b);
}

.ep-poster--locked {
  filter: grayscale(0.6);
}

.ep-code {
  font-size: 11px;
  font-weight: 800;
  letter-spacing: 0.06em;
  color: #fda4af;
}

.ep-emoji {
  font-size: 26px;
  line-height: 1;
}

.ep-main {
  flex: 1;
  min-width: 0;
}

.ep-meta {
  margin: 0 0 6px;
  font-size: 15px;
  font-weight: 800;
  color: #f8fafc;
  line-height: 1.35;
}

.ep-tagline {
  margin: 0;
  font-size: 13px;
  color: rgba(203, 213, 225, 0.82);
  line-height: 1.5;
}

.ep-cta {
  display: inline-block;
  margin-top: 10px;
  font-size: 13px;
  font-weight: 600;
  color: #fb7185;
}

.ep-badge {
  display: inline-block;
  margin-top: 10px;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  color: rgba(148, 163, 184, 0.95);
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(100, 116, 139, 0.35);
}

.foot-note {
  margin: 28px 4px 0;
  font-size: 12px;
  color: rgba(148, 163, 184, 0.75);
}
</style>
