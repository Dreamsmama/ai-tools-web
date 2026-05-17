<script setup>
import { RouterLink } from 'vue-router'
import CareerHeroSection from '../components/CareerHeroSection.vue'
import LifeExplorationSection from '../components/LifeExplorationSection.vue'
import WorkerPersonalityLabSection from '../components/WorkerPersonalityLabSection.vue'
import GrowthToolsSection from '../components/GrowthToolsSection.vue'
</script>

<template>
  <div class="page product-home">
    <header class="site-header">
      <p class="brand-kicker">AI 职场成长平台</p>
      <p class="brand-tagline">探索职业方向 · 兴趣爱好 · 下班生活 · 职场成长</p>
    </header>

    <CareerHeroSection variant="product" />

    <LifeExplorationSection />

    <WorkerPersonalityLabSection />

    <GrowthToolsSection />

    <footer class="site-footer">
      <RouterLink class="tools-library-btn" to="/tools">
        进入 AI 工具库
        <span class="tools-library-arrow" aria-hidden="true">→</span>
      </RouterLink>
      <p class="footer-note">全部场景工具合集，可在工具库中浏览</p>
    </footer>
  </div>
</template>

<style scoped>
.page {
  max-width: 800px;
  margin: 0 auto;
  padding: 20px 16px 48px;
  min-height: 100vh;
}

.site-header {
  margin: 0 12px 8px;
  padding: 0 4px;
}

.brand-kicker {
  margin: 0 0 6px;
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #6366f1;
}

.brand-tagline {
  margin: 0;
  font-size: 13px;
  line-height: 1.5;
  color: var(--text-muted);
}

.product-home :deep(.career-hero) {
  margin-bottom: 8px;
}

.site-footer {
  margin: 8px 12px 0;
  padding: 24px 0 8px;
  text-align: center;
}

.tools-library-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 28px;
  border-radius: 999px;
  font-size: 15px;
  font-weight: 600;
  text-decoration: none;
  color: #5b21b6;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(99, 102, 241, 0.3);
  box-shadow: var(--shadow-card);
  transition:
    transform var(--transition),
    box-shadow var(--transition),
    border-color var(--transition);
}

.tools-library-btn:hover {
  transform: translateY(-2px);
  border-color: rgba(99, 102, 241, 0.45);
  box-shadow: var(--shadow-float);
}

.tools-library-arrow {
  font-size: 16px;
  opacity: 0.8;
}

.footer-note {
  margin: 14px auto 0;
  max-width: 360px;
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-muted);
}
</style>
