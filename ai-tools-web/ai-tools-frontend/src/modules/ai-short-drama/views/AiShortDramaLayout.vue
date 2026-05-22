<script setup>
import { RouterLink, RouterView, useRoute } from 'vue-router'

const route = useRoute()

function tabClass(name) {
  const p = route.path
  if (name === 'generate') {
    const active = p === '/tools/ai-short-drama' || p === '/tools/ai-short-drama/'
    return ['tab', active ? 'tab--active' : '']
  }
  if (name === 'characters') {
    return ['tab', p.includes('/characters') ? 'tab--active' : '']
  }
  if (name === 'materials') {
    return ['tab', p.endsWith('/materials') ? 'tab--active' : '']
  }
  return ['tab']
}
</script>

<template>
  <div
    class="page"
    :class="{ 'page--wide': route.path.includes('/characters') || route.path.includes('/materials') }"
  >
    <nav class="top-nav">
      <RouterLink class="nav-link" to="/">← 首页</RouterLink>
      <RouterLink class="nav-link nav-link--muted" to="/tools">工具库</RouterLink>
    </nav>

    <header class="hero card">
      <p class="kicker">AI 职业图文成片</p>
      <h1 class="title">职业观察局生成器</h1>
      <p class="sub">
        粘贴文案，一键生成竖屏情绪短片——节奏与时长由系统自动计算，无需调参。
      </p>
    </header>

    <nav class="tabs card" aria-label="职业观察局功能导航">
      <RouterLink :class="tabClass('generate')" to="/tools/ai-short-drama">生成视频</RouterLink>
      <RouterLink :class="tabClass('characters')" to="/tools/ai-short-drama/characters">
        角色管理
      </RouterLink>
      <RouterLink :class="tabClass('materials')" to="/tools/ai-short-drama/materials">
        场景素材
      </RouterLink>
    </nav>

    <RouterView />
  </div>
</template>

<style scoped>
.page {
  max-width: 640px;
  margin: 0 auto;
  padding: 16px 14px 48px;
  min-height: 100vh;
}

.page--wide {
  max-width: 1080px;
}

.top-nav {
  display: flex;
  gap: 16px;
  padding: 0 2px 12px;
}

.nav-link {
  font-size: 14px;
  font-weight: 600;
  color: #6366f1;
  text-decoration: none;
}

.nav-link--muted {
  color: var(--text-muted);
}

.hero {
  margin-bottom: 12px;
}

.card {
  background: var(--surface-solid);
  border-radius: var(--radius);
  padding: 18px 16px;
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
}

.kicker {
  margin: 0 0 8px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #6366f1;
}

.title {
  margin: 0 0 8px;
  font-size: 22px;
  font-weight: 800;
  line-height: 1.35;
  color: var(--text);
}

.sub {
  margin: 0;
  font-size: 14px;
  line-height: 1.65;
  color: var(--text-muted);
}

.tabs {
  display: flex;
  gap: 6px;
  padding: 6px;
  margin-bottom: 16px;
}

.tab {
  flex: 1;
  text-align: center;
  padding: 10px 8px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 600;
  text-decoration: none;
  color: var(--text-muted);
  transition:
    background var(--transition),
    color var(--transition);
}

.tab--active {
  color: #5b21b6;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.14), rgba(168, 85, 247, 0.1));
  box-shadow: inset 0 0 0 1px rgba(99, 102, 241, 0.2);
}
</style>
