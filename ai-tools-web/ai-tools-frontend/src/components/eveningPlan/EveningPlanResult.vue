<script setup>
import { computed } from 'vue'

const props = defineProps({
  result: { type: Object, required: true },
})

const emit = defineEmits(['regenerate', 'edit', 'copy'])

const plans = computed(() => props.result?.plans || [])

function stars(score) {
  const n = Math.min(5, Math.max(1, Number(score) || 3))
  return '★'.repeat(n) + '☆'.repeat(5 - n)
}

const planLabels = ['方案一：吃什么', '方案二：做什么', '方案三：回家后怎么收尾']

function planLabel(idx, plan) {
  if (plan?.plan_type) return plan.plan_type
  return planLabels[idx] || `方案 ${idx + 1}`
}
</script>

<template>
  <div class="result">
    <section class="card mode-card">
      <p class="kicker">今晚推荐模式</p>
      <h2 class="mode-title">{{ result.mode || '为你定制的今晚' }}</h2>
    </section>

    <section class="card">
      <h2 class="block-title">适合你的今晚安排</h2>
      <article v-for="(plan, idx) in plans" :key="idx" class="plan-box">
        <h3 class="plan-title">{{ planLabel(idx, plan) }}</h3>
        <p v-if="plan.title" class="plan-headline">{{ plan.title }}</p>
        <dl class="plan-meta">
          <div v-if="plan.reason" class="meta-row">
            <dt>推荐理由</dt>
            <dd>{{ plan.reason }}</dd>
          </div>
          <div v-if="plan.actions?.length" class="meta-row">
            <dt>具体行动</dt>
            <dd>
              <ul class="action-list">
                <li v-for="(act, i) in plan.actions" :key="i">{{ act }}</li>
              </ul>
            </dd>
          </div>
          <div v-if="plan.cost" class="meta-row inline">
            <dt>预计花费</dt>
            <dd>{{ plan.cost }}</dd>
          </div>
          <div v-if="plan.duration" class="meta-row inline">
            <dt>预计耗时</dt>
            <dd>{{ plan.duration }}</dd>
          </div>
          <div v-if="plan.fit_score" class="meta-row inline">
            <dt>适合程度</dt>
            <dd class="stars" :aria-label="`${plan.fit_score} 星`">{{ stars(plan.fit_score) }}</dd>
          </div>
        </dl>
      </article>
    </section>

    <section v-if="result.avoid?.length" class="card warn-card">
      <h2 class="block-title">不建议你今晚做什么</h2>
      <ul class="bullet-list">
        <li v-for="(item, idx) in result.avoid" :key="idx">{{ item }}</li>
      </ul>
    </section>

    <section v-if="result.lazy_fallback" class="card soft-card">
      <h2 class="block-title">如果你只想躺平</h2>
      <p v-if="result.lazy_fallback.title" class="lazy-title">{{ result.lazy_fallback.title }}</p>
      <p class="lazy-desc">{{ result.lazy_fallback.description }}</p>
    </section>

    <section v-if="result.tomorrow_tips?.length" class="card">
      <h2 class="block-title">明天状态保护建议</h2>
      <ul class="bullet-list">
        <li v-for="(tip, idx) in result.tomorrow_tips" :key="idx">{{ tip }}</li>
      </ul>
    </section>

    <div class="actions">
      <button type="button" class="btn btn-gradient" @click="emit('regenerate')">重新生成</button>
      <button type="button" class="btn btn-outline" @click="emit('edit')">修改条件</button>
      <button type="button" class="btn btn-outline" @click="emit('copy')">复制今晚安排</button>
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

.mode-card {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(168, 85, 247, 0.06));
}

.kicker {
  margin: 0 0 6px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: #6366f1;
}

.mode-title {
  margin: 0;
  font-size: 20px;
  font-weight: 800;
  color: var(--text);
  line-height: 1.4;
}

.block-title {
  margin: 0 0 14px;
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
}

.plan-box {
  padding: 14px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(248, 250, 252, 0.85);
  margin-bottom: 12px;
}

.plan-box:last-child {
  margin-bottom: 0;
}

.plan-title {
  margin: 0 0 6px;
  font-size: 13px;
  font-weight: 700;
  color: #6366f1;
}

.plan-headline {
  margin: 0 0 12px;
  font-size: 16px;
  font-weight: 700;
  color: var(--text);
  line-height: 1.45;
}

.plan-meta {
  margin: 0;
}

.meta-row {
  margin-bottom: 10px;
}

.meta-row:last-child {
  margin-bottom: 0;
}

.meta-row dt {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 4px;
}

.meta-row dd {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text);
}

.meta-row.inline {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.meta-row.inline dt {
  margin-bottom: 0;
  flex-shrink: 0;
}

.action-list {
  margin: 0;
  padding-left: 18px;
}

.action-list li {
  margin-bottom: 4px;
}

.action-list li:last-child {
  margin-bottom: 0;
}

.stars {
  color: #f59e0b;
  letter-spacing: 1px;
}

.warn-card {
  background: linear-gradient(135deg, rgba(254, 243, 199, 0.5), rgba(255, 237, 213, 0.35));
  border-color: rgba(251, 191, 36, 0.3);
}

.soft-card {
  background: linear-gradient(135deg, rgba(224, 242, 254, 0.5), rgba(240, 249, 255, 0.6));
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

.btn-outline {
  border: 1px solid rgba(148, 163, 184, 0.4);
  background: rgba(255, 255, 255, 0.95);
  color: #4338ca;
}
</style>
