<script setup>
import { computed, onMounted } from 'vue'
import { RouterLink, useRoute } from 'vue-router'
import { getHotTopicBySlug } from '../data/gaokao/hotTopics.js'
import { getHotTopicArticle } from '../data/gaokao/hotTopicArticles.js'
import { getMajorById } from '../data/gaokao/majorsCatalog.js'
import { getCareerById } from '../data/careersCatalog.js'
import { trackEvent } from '../analytics.js'

const route = useRoute()
const slug = computed(() => String(route.params.slug || ''))
const topic = computed(() => getHotTopicBySlug(slug.value))
const article = computed(() => getHotTopicArticle(slug.value))

const relatedMajors = computed(() =>
  (article.value?.relatedMajorIds ?? []).map((id) => getMajorById(id)).filter(Boolean),
)
const relatedCareers = computed(() =>
  (article.value?.relatedCareerIds ?? []).map((id) => getCareerById(id)).filter(Boolean),
)

onMounted(() => {
  trackEvent('gaokao_hot_topic_view', {
    feature: 'gaokao',
    page: `/gaokao/topics/${slug.value}`,
    props: { slug: slug.value },
  })
})
</script>

<template>
  <div class="page">
    <RouterLink class="back" to="/gaokao">← 返回高考生专区</RouterLink>

    <template v-if="topic && article">
      <header class="hero" :class="`hero--${topic.tone}`">
        <span class="tag">{{ topic.tag }}</span>
        <h1 class="h1">{{ topic.title }}</h1>
        <p class="meta">约 {{ article.readMinutes }} 分钟阅读 · 更新 {{ article.updatedAt }}</p>
        <p class="lead">{{ topic.teaser }}</p>
      </header>

      <article v-for="(sec, i) in article.sections" :key="i" class="card">
        <h2 class="h2">{{ sec.heading }}</h2>
        <p v-for="(para, j) in sec.body" :key="j" class="para">{{ para }}</p>
      </article>

      <section class="card highlight">
        <h2 class="h2">划重点</h2>
        <ul class="takeaways">
          <li v-for="(t, i) in article.takeaways" :key="i">{{ t }}</li>
        </ul>
      </section>

      <section v-if="relatedMajors.length" class="card">
        <h2 class="h2">相关专业方向</h2>
        <div class="chips">
          <span v-for="m in relatedMajors" :key="m.id" class="chip">{{ m.name }}</span>
        </div>
      </section>

      <section v-if="relatedCareers.length" class="card">
        <h2 class="h2">相关职业</h2>
        <ul class="link-list">
          <li v-for="c in relatedCareers" :key="c.id">
            <RouterLink :to="`/career/${c.id}`">{{ c.name }}</RouterLink>
          </li>
        </ul>
      </section>

      <div class="footer-actions">
        <RouterLink class="btn-main btn-gradient" to="/gaokao/test">去做专业测试</RouterLink>
        <RouterLink class="btn-ghost" to="/gaokao">返回专区首页</RouterLink>
      </div>
    </template>

    <section v-else class="card empty">
      <p>未找到该话题，可能已下线。</p>
      <RouterLink to="/gaokao">返回高考生专区</RouterLink>
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
  color: #0891b2;
  text-decoration: none;
}

.hero {
  margin: 0 4px 16px;
  padding: 20px 18px;
  border-radius: var(--radius);
  border: 1px solid rgba(148, 163, 184, 0.28);
  background: var(--surface-solid);
  box-shadow: var(--shadow-card);
}

.hero--alert {
  border-color: rgba(248, 113, 113, 0.35);
  background: linear-gradient(135deg, #fff5f5, #fff);
}

.hero--insight {
  border-color: rgba(99, 102, 241, 0.3);
  background: linear-gradient(135deg, #eef2ff, #fff);
}

.hero--guide {
  border-color: rgba(20, 184, 166, 0.35);
  background: linear-gradient(135deg, #f0fdfa, #fff);
}

.tag {
  display: inline-block;
  margin-bottom: 10px;
  padding: 4px 10px;
  border-radius: 999px;
  font-size: 11px;
  font-weight: 700;
  color: #0891b2;
  background: rgba(6, 182, 212, 0.12);
}

.h1 {
  margin: 0 0 8px;
  font-size: 22px;
  font-weight: 800;
  line-height: 1.35;
  color: var(--text);
}

.meta {
  margin: 0 0 12px;
  font-size: 12px;
  color: var(--text-muted);
}

.lead {
  margin: 0;
  font-size: 15px;
  line-height: 1.65;
  color: var(--text);
}

.card {
  margin: 0 4px 14px;
  padding: 18px 16px;
  border-radius: var(--radius);
  background: var(--surface-solid);
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
}

.highlight {
  background: linear-gradient(135deg, rgba(224, 242, 254, 0.6), rgba(255, 255, 255, 0.98));
}

.h2 {
  margin: 0 0 10px;
  font-size: 16px;
  font-weight: 800;
  color: var(--text);
}

.para {
  margin: 0 0 10px;
  font-size: 14px;
  line-height: 1.75;
  color: var(--text);
}

.para:last-child {
  margin-bottom: 0;
}

.takeaways {
  margin: 0;
  padding-left: 18px;
  font-size: 14px;
  line-height: 1.7;
  color: var(--text);
}

.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.chip {
  padding: 6px 12px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  color: #5b21b6;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.link-list {
  margin: 0;
  padding: 0;
  list-style: none;
}

.link-list a {
  display: block;
  padding: 10px 0;
  font-weight: 600;
  color: #0891b2;
  text-decoration: none;
  border-top: 1px solid rgba(148, 163, 184, 0.2);
}

.link-list li:first-child a {
  border-top: none;
  padding-top: 0;
}

.footer-actions {
  margin: 20px 4px 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn-main {
  display: block;
  padding: 14px;
  text-align: center;
  border-radius: 14px;
  font-weight: 600;
  text-decoration: none;
  color: #fff;
}

.btn-ghost {
  display: block;
  padding: 12px;
  text-align: center;
  border-radius: 14px;
  font-weight: 600;
  text-decoration: none;
  color: var(--text-muted);
  border: 1px solid rgba(148, 163, 184, 0.35);
}

.empty {
  text-align: center;
  color: var(--text-muted);
}
</style>
