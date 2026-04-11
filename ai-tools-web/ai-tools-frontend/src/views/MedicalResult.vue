<script setup>
import { ref, onMounted } from 'vue'
import { RouterLink } from 'vue-router'

const STORAGE_KEY = 'consult_result'

const summary = ref([])
const questions = ref([])
const notes = ref([])

onMounted(() => {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    if (!raw) return
    const data = JSON.parse(raw)
    summary.value = Array.isArray(data?.summary) ? data.summary : []
    questions.value = Array.isArray(data?.questions) ? data.questions : []
    notes.value = Array.isArray(data?.notes) ? data.notes : []
  } catch (e) {
    console.error(e)
  }
})
</script>

<template>
  <div class="page">
    <header class="nav">
      <RouterLink class="back" to="/medical">← 返回编辑</RouterLink>
      <RouterLink class="back pill" to="/">首页</RouterLink>
    </header>

    <section class="card intro">
      <div class="intro-icon" aria-hidden="true">✓</div>
      <h1 class="h2">问诊准备结果</h1>
      <p class="sub">下面内容用于就医前整理与沟通准备。</p>
    </section>

    <section class="card block">
      <h2 class="block-head">
        <span class="num">①</span>关键信息整理
      </h2>
      <template v-if="summary.length">
        <div v-for="(item, idx) in summary" :key="'s-' + idx" class="list-item">
          {{ item }}
        </div>
      </template>
      <p v-else class="muted">暂无</p>
    </section>

    <section class="card block block-q">
      <h2 class="block-head">
        <span class="num">②</span>建议向医生询问
      </h2>
      <template v-if="questions.length">
        <div
          v-for="(item, idx) in questions"
          :key="'q-' + idx"
          class="list-item q-item"
        >
          <span class="q-badge">Q{{ idx + 1 }}</span>
          <span class="q-text">{{ item }}</span>
        </div>
      </template>
      <p v-else class="muted">暂无</p>
    </section>

    <section class="card block">
      <h2 class="block-head">
        <span class="num">③</span>沟通/准备提醒
      </h2>
      <template v-if="notes.length">
        <div v-for="(item, idx) in notes" :key="'n-' + idx" class="list-item note">
          {{ item }}
        </div>
      </template>
      <p v-else class="muted">暂无</p>
    </section>

    <p class="disclaimer">
      本工具仅用于健康信息整理与沟通准备，不构成医疗建议。
    </p>
  </div>
</template>

<style scoped>
.page {
  max-width: 720px;
  margin: 0 auto;
  padding: 16px 12px 40px;
  min-height: 100vh;
}

.nav {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 4px 4px 14px;
}

.back {
  font-size: 14px;
  font-weight: 500;
  color: #6366f1;
  text-decoration: none;
}

.back:hover {
  opacity: 0.85;
}

.back.pill {
  padding: 6px 14px;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.1);
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.card {
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-radius: 18px;
  padding: 18px 16px;
  margin-bottom: 14px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  box-shadow: 0 4px 24px rgba(15, 23, 42, 0.06);
}

.intro {
  text-align: center;
  padding: 22px 18px;
}

.intro-icon {
  width: 44px;
  height: 44px;
  margin: 0 auto 12px;
  line-height: 44px;
  font-size: 20px;
  border-radius: 14px;
  color: #fff;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  box-shadow: 0 10px 28px rgba(99, 102, 241, 0.35);
}

.h2 {
  font-size: 18px;
  font-weight: 800;
  margin: 0 0 8px;
  color: #0f172a;
  letter-spacing: -0.02em;
}

.sub {
  margin: 0;
  font-size: 13px;
  color: #64748b;
  line-height: 1.55;
}

.block-head {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 15px;
  font-weight: 700;
  margin: 0 0 14px;
  color: #0f172a;
}

.num {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 28px;
  height: 28px;
  font-size: 13px;
  font-weight: 800;
  color: #fff;
  border-radius: 8px;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.25);
}

.block-q .num {
  background: linear-gradient(135deg, #06b6d4, #6366f1);
}

.list-item {
  padding: 12px 14px;
  margin-bottom: 8px;
  border-radius: 12px;
  font-size: 15px;
  line-height: 1.55;
  color: #334155;
  background: rgba(248, 250, 252, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.15);
}

.list-item:last-child {
  margin-bottom: 0;
}

.q-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.q-badge {
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 800;
  padding: 4px 8px;
  border-radius: 8px;
  color: #5b21b6;
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.q-text {
  flex: 1;
}

.note {
  border-left: 3px solid #a855f7;
}

.muted {
  margin: 0;
  font-size: 14px;
  color: #94a3b8;
}

.disclaimer {
  margin: 8px 4px 0;
  padding: 14px 16px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(254, 243, 199, 0.55), rgba(255, 237, 213, 0.45));
  color: #92400e;
  font-size: 12px;
  line-height: 1.65;
  border: 1px solid rgba(251, 191, 36, 0.3);
}
</style>
