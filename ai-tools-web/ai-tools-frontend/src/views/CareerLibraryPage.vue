<script setup>
import { RouterLink } from 'vue-router'
import { listCareersForLibrary } from '../data/careersCatalog'

const careers = listCareersForLibrary()
</script>

<template>
  <div class="page">
    <RouterLink class="back" to="/">← 返回首页</RouterLink>

    <header class="header">
      <h1 class="h1">职业观察库</h1>
      <p class="sub">共 {{ careers.length }} 个职业卡片，点击查看真实工作内容、场景与 AI 影响（本地 Mock）。</p>
    </header>

    <div class="list">
      <RouterLink v-for="c in careers" :key="c.id" class="article-link" :to="`/career/${c.id}`">
        <article class="article-card">
          <div class="accent" aria-hidden="true" />
          <div class="row">
            <h2 class="title">{{ c.name }}</h2>
            <span class="tag">{{ c.libraryTag }}</span>
          </div>
          <p class="excerpt">{{ c.libraryTeaser }}</p>
        </article>
      </RouterLink>
    </div>

    <RouterLink class="btn-outline" to="/career-test">去做职业倾向测试</RouterLink>
  </div>
</template>

<style scoped>
.page {
  max-width: 720px;
  margin: 0 auto;
  padding: 20px 16px 40px;
  min-height: 100vh;
}

.back {
  display: inline-block;
  margin: 0 12px 16px;
  font-size: 14px;
  font-weight: 600;
  color: var(--accent-a);
  text-decoration: none;
}

.back:hover {
  text-decoration: underline;
}

.header {
  margin: 0 12px 18px;
}

.h1 {
  font-size: 22px;
  font-weight: 800;
  margin: 0 0 8px;
  letter-spacing: -0.02em;
  color: var(--text);
}

.sub {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-muted);
}

.list {
  margin: 0 12px;
}

.article-link {
  text-decoration: none;
  color: inherit;
  display: block;
  margin-bottom: 12px;
}

.article-card {
  position: relative;
  overflow: hidden;
  padding: 18px 18px 18px 22px;
  border-radius: var(--radius);
  background: var(--surface-solid);
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
  transition:
    transform var(--transition),
    box-shadow var(--transition);
}

.article-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-float);
}

.accent {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, #6366f1, #a855f7, #06b6d4);
  border-radius: 4px 0 0 4px;
}

.row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.title {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
  line-height: 1.35;
  color: var(--text);
}

.tag {
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 600;
  padding: 5px 11px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(168, 85, 247, 0.1));
  color: #5b21b6;
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.excerpt {
  margin: 10px 0 0;
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.55;
}

.btn-outline {
  display: block;
  margin: 20px 24px 0;
  padding: 13px 18px;
  text-align: center;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  text-decoration: none;
  color: #5b21b6;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(99, 102, 241, 0.28);
  transition:
    transform var(--transition),
    box-shadow var(--transition);
}

.btn-outline:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 22px rgba(99, 102, 241, 0.12);
}
</style>
