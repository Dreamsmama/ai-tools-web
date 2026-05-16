<script setup>
import { RouterLink } from 'vue-router'
import { homeCareerTags } from '../data/homeCareerTags.js'
import { trackEvent } from '../analytics.js'

const careerTags = homeCareerTags

function onHeroTestClick() {
  trackEvent('career_hero_test_click', {
    feature: 'career',
    page: '/',
    props: { target: '/career-test' },
  })
}

function onHeroLibraryClick() {
  trackEvent('career_hero_library_click', {
    feature: 'career',
    page: '/',
    props: { target: '/career-library' },
  })
}

function onHeroExperienceClick() {
  trackEvent('career_hero_experience_click', {
    feature: 'career',
    page: '/',
    props: { target: '/career-experience' },
  })
}

function onHeroGaokaoClick() {
  trackEvent('career_hero_gaokao_click', {
    feature: 'gaokao',
    page: '/',
    props: { target: '/gaokao' },
  })
}
</script>

<template>
  <section class="career-hero" aria-labelledby="career-hero-title">
    <div class="career-hero-glow career-hero-glow-a" aria-hidden="true" />
    <div class="career-hero-glow career-hero-glow-b" aria-hidden="true" />
    <div class="career-hero-grid" aria-hidden="true" />

    <p class="career-hero-kicker">AI 职业成长平台</p>
    <h1 id="career-hero-title" class="career-hero-title">
      <span class="gradient-text">AI 时代</span>，你适合什么专业和职业？
    </h1>
    <p class="career-hero-sub">
      通过 3 分钟职业倾向测试，获得适合你的专业方向、职业建议与未来发展分析。
    </p>

    <div class="career-hero-actions">
      <RouterLink class="career-btn career-btn-primary btn-gradient" to="/career-test" @click="onHeroTestClick">
        开始职业测试
      </RouterLink>
      <RouterLink class="career-btn career-btn-secondary" to="/career-library" @click="onHeroLibraryClick">
        职业观察库
      </RouterLink>
      <RouterLink class="career-btn career-btn-experience" to="/career-experience" @click="onHeroExperienceClick">
        AI 职业体验馆
      </RouterLink>
      <RouterLink class="career-btn career-btn-gaokao" to="/gaokao" @click="onHeroGaokaoClick">
        高考生专区
      </RouterLink>
    </div>

    <div class="career-tag-cloud" role="list" aria-label="热门职业方向">
      <span v-for="tag in careerTags" :key="tag" class="career-tag" role="listitem">{{ tag }}</span>
    </div>
  </section>
</template>

<style scoped>
.career-hero {
  position: relative;
  overflow: hidden;
  margin: 0 12px 20px;
  padding: 28px 22px 26px;
  border-radius: var(--radius);
  background: linear-gradient(
    145deg,
    rgba(255, 255, 255, 0.95) 0%,
    rgba(238, 242, 255, 0.88) 45%,
    rgba(250, 245, 255, 0.92) 100%
  );
  border: var(--border-soft);
  box-shadow:
    var(--shadow-card),
    0 0 0 1px rgba(99, 102, 241, 0.06) inset;
}

.career-hero-glow {
  position: absolute;
  pointer-events: none;
  border-radius: 50%;
  filter: blur(48px);
}

.career-hero-glow-a {
  top: -30%;
  right: -15%;
  width: 55%;
  height: 70%;
  background: rgba(99, 102, 241, 0.2);
}

.career-hero-glow-b {
  bottom: -25%;
  left: -10%;
  width: 45%;
  height: 55%;
  background: rgba(168, 85, 247, 0.14);
}

.career-hero-grid {
  position: absolute;
  inset: 0;
  opacity: 0.04;
  background-image:
    linear-gradient(rgba(99, 102, 241, 0.9) 1px, transparent 1px),
    linear-gradient(90deg, rgba(99, 102, 241, 0.9) 1px, transparent 1px);
  background-size: 22px 22px;
  pointer-events: none;
}

.career-hero-kicker {
  position: relative;
  margin: 0 0 10px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.14em;
  text-transform: uppercase;
  color: #6366f1;
}

.career-hero-title {
  position: relative;
  margin: 0 0 12px;
  font-size: 22px;
  font-weight: 800;
  line-height: 1.35;
  letter-spacing: -0.02em;
  color: var(--text);
}

.gradient-text {
  background: linear-gradient(135deg, #6366f1, #8b5cf6, #a855f7);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.career-hero-sub {
  position: relative;
  margin: 0 0 22px;
  font-size: 14px;
  line-height: 1.65;
  color: var(--text-muted);
}

.career-hero-actions {
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 22px;
}

@media (min-width: 420px) {
  .career-hero-actions {
    flex-direction: row;
    flex-wrap: wrap;
    align-items: stretch;
  }
}

.career-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  padding: 13px 18px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  text-decoration: none;
  text-align: center;
  transition:
    transform var(--transition),
    box-shadow var(--transition),
    background var(--transition),
    border-color var(--transition);
  flex: 1;
  min-width: 0;
}

.career-btn-primary {
  color: #fff;
  border: none;
}

.career-btn-secondary {
  color: #5b21b6;
  background: rgba(255, 255, 255, 0.75);
  border: 1px solid rgba(99, 102, 241, 0.28);
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

.career-btn-secondary:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.92);
  border-color: rgba(99, 102, 241, 0.4);
  box-shadow: 0 8px 24px rgba(99, 102, 241, 0.12);
}

.career-btn-secondary:active {
  transform: translateY(0);
}

.career-btn-experience {
  color: #0f766e;
  background: rgba(240, 253, 250, 0.95);
  border: 1px solid rgba(20, 184, 166, 0.35);
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

.career-btn-experience:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.98);
  border-color: rgba(20, 184, 166, 0.5);
  box-shadow: 0 8px 24px rgba(20, 184, 166, 0.12);
}

.career-btn-gaokao {
  color: #0e7490;
  background: rgba(224, 242, 254, 0.95);
  border: 1px solid rgba(6, 182, 212, 0.35);
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

.career-btn-gaokao:hover {
  transform: translateY(-2px);
  background: rgba(255, 255, 255, 0.98);
  border-color: rgba(6, 182, 212, 0.5);
  box-shadow: 0 8px 24px rgba(6, 182, 212, 0.12);
}

.career-tag-cloud {
  position: relative;
  display: flex;
  flex-wrap: nowrap;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 4px;
  -webkit-overflow-scrolling: touch;
  scrollbar-width: none;
}

.career-tag-cloud::-webkit-scrollbar {
  display: none;
}

.career-tag {
  display: inline-block;
  flex-shrink: 0;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 600;
  color: #5b21b6;
  background: linear-gradient(
    135deg,
    rgba(99, 102, 241, 0.1),
    rgba(168, 85, 247, 0.08)
  );
  border: 1px solid rgba(99, 102, 241, 0.18);
  border-radius: 999px;
  transition:
    transform var(--transition),
    box-shadow var(--transition),
    border-color var(--transition),
    background var(--transition);
}

.career-tag:hover {
  transform: translateY(-2px) scale(1.02);
  border-color: rgba(99, 102, 241, 0.32);
  box-shadow: 0 6px 16px rgba(99, 102, 241, 0.12);
  background: linear-gradient(
    135deg,
    rgba(99, 102, 241, 0.14),
    rgba(168, 85, 247, 0.12)
  );
}
</style>
