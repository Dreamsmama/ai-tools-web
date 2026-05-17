<script setup>
import { RouterLink } from 'vue-router'
import { WORKER_LAB_SERIES } from '../data/careerExperience/workerLabSeries.js'
import { trackEvent } from '../analytics.js'

const seriesList = WORKER_LAB_SERIES

function onEpisodeClick(seriesId, episode) {
  trackEvent('career_experience_pick', {
    feature: 'career_experience',
    page: '/',
    props: {
      series_id: seriesId,
      episode_id: episode.id,
      experience_key: episode.experienceKey,
      source: 'home_lab_section',
    },
  })
}
</script>

<template>
  <section class="lab-section" aria-labelledby="worker-lab-title">
    <div class="lab-glow lab-glow-a" aria-hidden="true" />
    <div class="lab-glow lab-glow-b" aria-hidden="true" />

    <header class="lab-head">
      <p class="lab-kicker">🎭 打工人体验实验室</p>
      <h2 id="worker-lab-title" class="lab-title">像追剧一样，体验真实又荒诞的打工人生</h2>
      <p class="lab-sub">程序员、HR、产品经理……一集一集看清职场里的真实处境。</p>
    </header>

    <div v-for="series in seriesList" :key="series.id" class="series-block">
      <p class="series-label">{{ series.title }}</p>

      <ul class="episode-list" role="list">
        <li v-for="ep in series.episodes" :key="ep.id" class="episode-li">
          <RouterLink
            v-if="ep.status === 'open'"
            class="episode-card"
            :to="ep.to"
            @click="onEpisodeClick(series.id, ep)"
          >
            <div class="episode-poster" :class="`episode-poster--${series.id}`" aria-hidden="true">
              <span class="episode-code">{{ ep.code }}</span>
              <span class="episode-emoji">{{ ep.posterEmoji }}</span>
            </div>
            <div class="episode-body">
              <p class="episode-meta">{{ ep.code }} · {{ ep.title }}</p>
              <p class="episode-tagline">{{ ep.tagline }}</p>
              <span class="episode-cta">开始追剧 ›</span>
            </div>
          </RouterLink>

          <div v-else class="episode-card episode-card--locked" aria-disabled="true">
            <div class="episode-poster episode-poster--locked" aria-hidden="true">
              <span class="episode-code">{{ ep.code }}</span>
              <span class="episode-emoji">{{ ep.posterEmoji }}</span>
            </div>
            <div class="episode-body">
              <p class="episode-meta">{{ ep.code }} · {{ ep.title }}</p>
              <p class="episode-tagline">{{ ep.tagline }}</p>
              <span class="episode-badge">开发中</span>
            </div>
          </div>
        </li>
      </ul>
    </div>

    <RouterLink class="lab-more" to="/worker-lab">查看更多剧集 ›</RouterLink>
  </section>
</template>

<style scoped>
.lab-section {
  position: relative;
  overflow: hidden;
  margin: 0 12px 28px;
  padding: 26px 20px 22px;
  border-radius: calc(var(--radius) + 4px);
  background: linear-gradient(
    155deg,
    #0f172a 0%,
    #1e1b4b 42%,
    #312e81 78%,
    #1e293b 100%
  );
  border: 1px solid rgba(148, 163, 184, 0.2);
  box-shadow:
    0 24px 48px rgba(15, 23, 42, 0.35),
    inset 0 1px 0 rgba(255, 255, 255, 0.06);
}

.lab-glow {
  position: absolute;
  pointer-events: none;
  border-radius: 50%;
  filter: blur(56px);
}

.lab-glow-a {
  top: -20%;
  right: -10%;
  width: 50%;
  height: 55%;
  background: rgba(244, 63, 94, 0.22);
}

.lab-glow-b {
  bottom: -15%;
  left: -8%;
  width: 42%;
  height: 48%;
  background: rgba(168, 85, 247, 0.18);
}

.lab-head {
  position: relative;
  margin-bottom: 18px;
}

.lab-kicker {
  margin: 0 0 10px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.06em;
  color: #fda4af;
}

.lab-title {
  margin: 0 0 10px;
  font-size: 20px;
  font-weight: 800;
  line-height: 1.35;
  letter-spacing: -0.02em;
  color: #f8fafc;
}

.lab-sub {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: rgba(226, 232, 240, 0.78);
}

.series-block + .series-block {
  margin-top: 16px;
}

.series-label {
  position: relative;
  margin: 0 0 10px;
  font-size: 13px;
  font-weight: 800;
  color: #e2e8f0;
}

.episode-list {
  position: relative;
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.episode-card {
  display: flex;
  gap: 14px;
  padding: 14px;
  border-radius: 16px;
  text-decoration: none;
  color: inherit;
  background: rgba(15, 23, 42, 0.55);
  border: 1px solid rgba(148, 163, 184, 0.22);
  transition:
    transform var(--transition),
    border-color var(--transition),
    box-shadow var(--transition);
}

.episode-card:hover {
  transform: translateY(-3px);
  border-color: rgba(251, 113, 133, 0.45);
  box-shadow: 0 16px 32px rgba(0, 0, 0, 0.28);
}

.episode-card--locked {
  opacity: 0.5;
  cursor: not-allowed;
}

.episode-poster {
  flex-shrink: 0;
  width: 72px;
  min-height: 88px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 10px 8px;
  border: 1px solid rgba(148, 163, 184, 0.25);
}

.episode-poster--developer {
  background: linear-gradient(160deg, #1e3a5f, #0f172a);
}

.episode-poster--hr {
  background: linear-gradient(160deg, #4c1d95, #1e1b4b);
}

.episode-poster--locked {
  filter: grayscale(0.55);
}

.episode-code {
  font-size: 10px;
  font-weight: 800;
  letter-spacing: 0.06em;
  color: #fda4af;
}

.episode-emoji {
  font-size: 28px;
  line-height: 1;
}

.episode-body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.episode-meta {
  margin: 0;
  font-size: 15px;
  font-weight: 800;
  color: #f8fafc;
  line-height: 1.3;
}

.episode-tagline {
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
  color: rgba(203, 213, 225, 0.85);
  flex: 1;
}

.episode-cta {
  margin-top: 6px;
  font-size: 13px;
  font-weight: 600;
  color: #fb7185;
}

.episode-badge {
  margin-top: 6px;
  align-self: flex-start;
  padding: 3px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  color: rgba(148, 163, 184, 0.95);
  background: rgba(30, 41, 59, 0.8);
  border: 1px solid rgba(100, 116, 139, 0.35);
}

.lab-more {
  position: relative;
  display: inline-block;
  margin-top: 18px;
  font-size: 13px;
  font-weight: 600;
  color: rgba(253, 164, 175, 0.95);
  text-decoration: none;
}

.lab-more:hover {
  color: #fecdd3;
}
</style>
