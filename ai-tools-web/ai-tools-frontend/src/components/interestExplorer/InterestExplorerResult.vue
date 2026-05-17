<script setup>
import { computed } from 'vue'

const props = defineProps({
  result: { type: Object, required: true },
})

const emit = defineEmits(['regenerate', 'edit', 'copy'])

const personality = computed(() => props.result?.personality || {})
const interests = computed(() => props.result?.interests || [])

function stars(n) {
  const score = Math.min(5, Math.max(1, Number(n) || 3))
  return '★'.repeat(score) + '☆'.repeat(5 - score)
}

function levelClass(level) {
  if (level === '高') return 'level-high'
  if (level === '中') return 'level-mid'
  return 'level-low'
}
</script>

<template>
  <div class="result">
    <section class="card hero-card">
      <p class="kicker">你的兴趣人格类型</p>
      <h2 class="type-title">{{ personality.type_title || '探索中' }}</h2>
      <p v-if="personality.analysis" class="para">{{ personality.analysis }}</p>
      <div v-if="personality.why_past_failed" class="insight-box">
        <p class="insight-label">为什么以前容易坚持不下去</p>
        <p class="insight-text">{{ personality.why_past_failed }}</p>
      </div>
    </section>

    <section class="card">
      <h2 class="block-title">最适合你的兴趣推荐</h2>
      <article v-for="(item, idx) in interests" :key="idx" class="interest-card">
        <div class="interest-head">
          <span class="interest-index">{{ idx + 1 }}</span>
          <h3 class="interest-name">{{ item.name }}</h3>
        </div>
        <p v-if="item.why_fit" class="why-fit">{{ item.why_fit }}</p>
        <div class="tags">
          <span class="tag">
            入门难度 <strong class="stars">{{ stars(item.difficulty) }}</strong>
          </span>
          <span class="tag" :class="levelClass(item.cost_level)">花费 {{ item.cost_level }}</span>
          <span class="tag" :class="levelClass(item.social_level)">社交 {{ item.social_level }}</span>
        </div>
        <dl class="detail-list">
          <div v-if="item.long_term" class="detail-row">
            <dt>长期坚持</dt>
            <dd>{{ item.long_term }}</dd>
          </div>
          <div v-if="item.best_time" class="detail-row">
            <dt>适合开始</dt>
            <dd>{{ item.best_time }}</dd>
          </div>
          <div v-if="item.starter_tip" class="detail-row tip-row">
            <dt>新手入门</dt>
            <dd>{{ item.starter_tip }}</dd>
          </div>
        </dl>
      </article>
    </section>

    <section v-if="result.avoid?.length" class="card warn-card">
      <h2 class="block-title">不建议你尝试的兴趣</h2>
      <ul class="bullet-list">
        <li v-for="(item, idx) in result.avoid" :key="idx">{{ item }}</li>
      </ul>
    </section>

    <section v-if="result.week_plan?.length" class="card week-card">
      <h2 class="block-title">一周兴趣体验建议</h2>
      <div class="week-list">
        <div v-for="(w, idx) in result.week_plan" :key="idx" class="week-item">
          <span class="week-day">{{ w.day }}</span>
          <span class="week-act">{{ w.activity }}</span>
        </div>
      </div>
    </section>

    <section v-if="result.lazy_fallback" class="card soft-card">
      <h2 class="block-title">如果你完全不想动</h2>
      <p v-if="result.lazy_fallback.title" class="lazy-title">{{ result.lazy_fallback.title }}</p>
      <p class="lazy-desc">{{ result.lazy_fallback.description }}</p>
    </section>

    <div class="actions">
      <button type="button" class="btn btn-gradient" @click="emit('regenerate')">重新生成</button>
      <button type="button" class="btn btn-outline" @click="emit('edit')">修改条件</button>
      <button type="button" class="btn btn-outline" @click="emit('copy')">一键复制</button>
    </div>
  </div>
</template>

<style scoped>
.result {
  display: flex;
  flex-direction: column;
}

.card {
  background: var(--surface-solid);
  border-radius: var(--radius);
  padding: 18px 16px;
  margin-bottom: 12px;
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
}

.hero-card {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1), rgba(52, 211, 153, 0.06));
  border-color: rgba(16, 185, 129, 0.2);
}

.kicker {
  margin: 0 0 6px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #059669;
}

.type-title {
  margin: 0 0 10px;
  font-size: 20px;
  font-weight: 800;
  color: var(--text);
  line-height: 1.35;
}

.para {
  margin: 0 0 12px;
  font-size: 14px;
  line-height: 1.65;
  color: var(--text);
}

.insight-box {
  padding: 12px 14px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.75);
  border: 1px dashed rgba(16, 185, 129, 0.35);
}

.insight-label {
  margin: 0 0 6px;
  font-size: 12px;
  font-weight: 600;
  color: #047857;
}

.insight-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-muted);
}

.block-title {
  margin: 0 0 14px;
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
}

.interest-card {
  padding: 14px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  background: rgba(248, 250, 252, 0.9);
  margin-bottom: 12px;
}

.interest-card:last-child {
  margin-bottom: 0;
}

.interest-head {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.interest-index {
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #10b981, #34d399);
  flex-shrink: 0;
}

.interest-name {
  margin: 0;
  font-size: 17px;
  font-weight: 700;
  color: var(--text);
}

.why-fit {
  margin: 0 0 10px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-muted);
}

.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 12px;
}

.tag {
  font-size: 12px;
  padding: 4px 10px;
  border-radius: 999px;
  background: rgba(241, 245, 249, 0.95);
  border: 1px solid rgba(148, 163, 184, 0.25);
  color: var(--text-muted);
}

.tag strong.stars {
  color: #f59e0b;
  font-weight: 700;
  letter-spacing: 0.5px;
}

.tag.level-low {
  background: rgba(16, 185, 129, 0.1);
  color: #047857;
  border-color: rgba(16, 185, 129, 0.25);
}

.tag.level-mid {
  background: rgba(99, 102, 241, 0.1);
  color: #4338ca;
  border-color: rgba(99, 102, 241, 0.25);
}

.tag.level-high {
  background: rgba(249, 115, 22, 0.1);
  color: #c2410c;
  border-color: rgba(249, 115, 22, 0.25);
}

.detail-list {
  margin: 0;
}

.detail-row {
  margin-bottom: 8px;
}

.detail-row:last-child {
  margin-bottom: 0;
}

.detail-row dt {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 2px;
}

.detail-row dd {
  margin: 0;
  font-size: 14px;
  line-height: 1.55;
  color: var(--text);
}

.tip-row dd {
  color: #047857;
}

.warn-card {
  background: linear-gradient(135deg, rgba(254, 243, 199, 0.5), rgba(255, 237, 213, 0.35));
  border-color: rgba(251, 191, 36, 0.3);
}

.week-card {
  background: linear-gradient(135deg, rgba(224, 242, 254, 0.45), rgba(240, 249, 255, 0.6));
}

.week-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.week-item {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  padding: 12px;
  border-radius: 12px;
  background: rgba(255, 255, 255, 0.85);
  border: 1px solid rgba(148, 163, 184, 0.2);
}

.week-day {
  flex-shrink: 0;
  min-width: 44px;
  font-size: 13px;
  font-weight: 700;
  color: #059669;
}

.week-act {
  font-size: 14px;
  line-height: 1.55;
  color: var(--text);
}

.soft-card {
  background: linear-gradient(135deg, rgba(236, 253, 245, 0.7), rgba(209, 250, 229, 0.5));
  border-color: rgba(16, 185, 129, 0.2);
}

.bullet-list {
  margin: 0;
  padding-left: 18px;
  font-size: 14px;
  line-height: 1.65;
  color: var(--text);
}

.bullet-list li {
  margin-bottom: 8px;
}

.bullet-list li:last-child {
  margin-bottom: 0;
}

.lazy-title {
  margin: 0 0 8px;
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
}

.lazy-desc {
  margin: 0;
  font-size: 14px;
  line-height: 1.65;
  color: var(--text-muted);
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 4px;
}

.btn {
  width: 100%;
  padding: 14px 16px;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
}

.btn-gradient {
  background: linear-gradient(135deg, #10b981 0%, #34d399 55%, #6ee7b7 100%) !important;
  box-shadow: 0 8px 24px rgba(16, 185, 129, 0.28) !important;
}

.btn-outline {
  border: 1px solid rgba(148, 163, 184, 0.4);
  background: rgba(255, 255, 255, 0.95);
  color: #047857;
}
</style>
