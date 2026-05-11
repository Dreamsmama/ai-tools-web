<script setup>
import { computed, watch } from 'vue'
import { useRoute, RouterLink } from 'vue-router'
import { trackEvent } from '../analytics.js'
import { getCareerById } from '../data/careersCatalog'

const route = useRoute()
const career = computed(() => getCareerById(String(route.params.id)))

watch(
  () => route.params.id,
  (id) => {
    if (!id) return
    const sid = String(id)
    trackEvent('career_detail_view', {
      feature: 'career_library',
      page: `/career/${sid}`,
      props: { career_id: sid },
    })
  },
  { immediate: true },
)
</script>

<template>
  <div class="page">
    <RouterLink class="back" to="/career-library">← 返回职业库</RouterLink>

    <template v-if="career">
      <header class="card hero">
        <div class="glow" aria-hidden="true" />
        <span class="tag">{{ career.libraryTag }}</span>
        <h1 class="h1">{{ career.name }}</h1>
        <p class="truth">{{ career.oneLineTruth }}</p>
      </header>

      <section class="card">
        <h2 class="h2">真实工作内容</h2>
        <p class="para">{{ career.realWork }}</p>
      </section>

      <section class="card">
        <h2 class="h2">常见工作场景</h2>
        <ul class="bullets">
          <li v-for="(s, i) in career.scenarios" :key="i">{{ s }}</li>
        </ul>
      </section>

      <section class="card">
        <h2 class="h2">适合什么样的人</h2>
        <p class="para">{{ career.suitableFor }}</p>
      </section>

      <section class="card">
        <h2 class="h2">不太适合什么样的人</h2>
        <p class="para">{{ career.notSuitableFor }}</p>
      </section>

      <section class="card">
        <h2 class="h2">AI 正在怎么影响这个职业</h2>
        <p class="para">{{ career.aiImpact }}</p>
      </section>

      <section class="card">
        <h2 class="h2">入门学习建议</h2>
        <p class="para">{{ career.learningTips }}</p>
      </section>

      <RouterLink class="btn-back-lib btn-gradient" to="/career-library">返回职业观察库</RouterLink>

      <p class="mock-note">内容为前端 Mock，仅供参考，不构成职业或教育建议。</p>
    </template>

    <div v-else class="card empty">
      <h1 class="h1">未找到该职业</h1>
      <p class="sub">请从职业库选择卡片进入，或检查链接是否正确。</p>
      <RouterLink class="btn btn-gradient" to="/career-library">返回职业观察库</RouterLink>
    </div>
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

.card {
  position: relative;
  overflow: hidden;
  background: var(--surface-solid);
  border-radius: var(--radius);
  padding: 22px 20px;
  margin: 0 12px 12px;
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
}

.hero {
  padding: 24px 20px;
}

.glow {
  position: absolute;
  top: -40%;
  right: -15%;
  width: 55%;
  height: 100%;
  background: radial-gradient(circle, rgba(99, 102, 241, 0.12) 0%, transparent 70%);
  pointer-events: none;
}

.tag {
  position: relative;
  display: inline-block;
  margin: 0 0 12px;
  font-size: 11px;
  font-weight: 600;
  padding: 5px 11px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(168, 85, 247, 0.1));
  color: #5b21b6;
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.h1 {
  position: relative;
  font-size: 22px;
  font-weight: 800;
  margin: 0 0 12px;
  line-height: 1.35;
  letter-spacing: -0.02em;
  color: var(--text);
}

.truth {
  position: relative;
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  line-height: 1.6;
  color: #4338ca;
}

.h2 {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 12px;
  color: var(--text);
}

.para {
  margin: 0;
  font-size: 15px;
  line-height: 1.75;
  color: var(--text);
}

.bullets {
  margin: 0;
  padding-left: 1.1rem;
  font-size: 15px;
  line-height: 1.75;
  color: var(--text);
}

.bullets li {
  margin-bottom: 6px;
}

.btn-back-lib {
  display: block;
  margin: 4px 12px 0;
  padding: 14px 18px;
  text-align: center;
  border-radius: 14px;
  text-decoration: none;
  font-size: 16px;
  font-weight: 600;
  color: #fff;
}

.mock-note {
  margin: 16px 16px 0;
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
}

.empty .sub {
  margin: 0 0 18px;
  font-size: 14px;
  color: var(--text-muted);
}

.btn {
  display: inline-block;
  padding: 12px 20px;
  border-radius: 12px;
  text-decoration: none;
  font-size: 15px;
  font-weight: 600;
  border: none;
}
</style>
