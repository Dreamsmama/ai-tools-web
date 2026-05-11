<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import { careerTestQuestions, DIMENSION_ORDER, dimensionLabels } from '../data/careerTestQuestions'
import { buildTestResult } from '../lib/careerTestEngine'

const phase = ref(/** @type {'quiz'|'result'} */ ('quiz'))
const currentIndex = ref(0)
/** @type {import('vue').Ref<(number|null)[]> */
const answers = ref(careerTestQuestions.map(() => null))

const total = careerTestQuestions.length

const currentQuestion = computed(() => careerTestQuestions[currentIndex.value])
const currentAnswer = computed(() => answers.value[currentIndex.value])
const canGoNext = computed(() => currentAnswer.value !== null && currentAnswer.value !== undefined)
const allAnswered = computed(() => answers.value.every((a) => a !== null && a !== undefined))

/** @type {import('vue').Ref<ReturnType<typeof buildTestResult> | null>} */
const result = ref(null)

const maxScore = computed(() => {
  if (!result.value) return 1
  return Math.max(1, ...DIMENSION_ORDER.map((d) => result.value.scores[d] ?? 0))
})

function selectOption(optIdx) {
  const copy = [...answers.value]
  copy[currentIndex.value] = optIdx
  answers.value = copy
}

function goPrev() {
  if (currentIndex.value > 0) currentIndex.value -= 1
}

function goNext() {
  if (!canGoNext.value || currentIndex.value >= total - 1) return
  currentIndex.value += 1
}

function submitQuiz() {
  if (!allAnswered.value) return
  result.value = buildTestResult(answers.value)
  phase.value = 'result'
}

function restart() {
  phase.value = 'quiz'
  currentIndex.value = 0
  answers.value = careerTestQuestions.map(() => null)
  result.value = null
}
</script>

<template>
  <div class="page">
    <RouterLink class="back" to="/">← 返回首页</RouterLink>

    <template v-if="phase === 'quiz'">
      <header class="intro card">
        <p class="kicker">职业倾向测试</p>
        <h1 class="h1">共 {{ total }} 题，约 3 分钟</h1>
        <p class="sub">每题单选，需选择后才能进入下一题；可随时返回修改。</p>
      </header>

      <section class="card quiz-card">
        <div class="progress-row">
          <span class="progress-text">{{ currentIndex + 1 }} / {{ total }}</span>
          <div class="progress-bar" role="progressbar" :aria-valuenow="currentIndex + 1" :aria-valuemax="total">
            <div class="progress-fill" :style="{ width: `${((currentIndex + 1) / total) * 100}%` }" />
          </div>
        </div>

        <h2 class="q-title">{{ currentQuestion.question }}</h2>

        <div class="options" role="radiogroup" :aria-label="currentQuestion.question">
          <button
            v-for="(opt, idx) in currentQuestion.options"
            :key="idx"
            type="button"
            class="option"
            :class="{ selected: currentAnswer === idx }"
            role="radio"
            :aria-checked="currentAnswer === idx"
            @click="selectOption(idx)"
          >
            <span class="option-idx">{{ String.fromCharCode(65 + idx) }}</span>
            <span class="option-label">{{ opt.label }}</span>
          </button>
        </div>

        <div class="nav-row">
          <button type="button" class="btn-ghost" :disabled="currentIndex === 0" @click="goPrev">上一步</button>
          <button
            v-if="currentIndex < total - 1"
            type="button"
            class="btn-primary btn-gradient"
            :disabled="!canGoNext"
            @click="goNext"
          >
            下一步
          </button>
          <button
            v-else
            type="button"
            class="btn-primary btn-gradient"
            :disabled="!allAnswered"
            @click="submitQuiz"
          >
            提交并查看结果
          </button>
        </div>
      </section>
    </template>

    <template v-else-if="result">
      <section class="card result-hero">
        <p class="kicker">测试结果</p>
        <h1 class="h1">你的职业倾向画像</h1>
        <p class="sub">以下为本地规则根据你的选择生成，仅供参考，不构成职业或心理诊断。</p>
      </section>

      <section class="card">
        <h2 class="h2">维度得分</h2>
        <ul class="score-list">
          <li v-for="d in DIMENSION_ORDER" :key="d" class="score-row">
            <span class="score-name">{{ dimensionLabels[d] }}</span>
            <div class="score-bar-wrap">
              <div class="score-bar" :style="{ width: `${((result.scores[d] ?? 0) / maxScore) * 100}%` }" />
            </div>
            <span class="score-num">{{ result.scores[d] ?? 0 }}</span>
          </li>
        </ul>
      </section>

      <section class="card highlight">
        <h2 class="h2">主要职业倾向</h2>
        <p class="lead">{{ result.primaryLabel }}</p>
        <h2 class="h2 mt">第二职业倾向</h2>
        <p class="lead">{{ result.secondaryLabel }}</p>
        <p v-if="result.blended" class="blend-note">前两项得分接近，推荐列表已为你做混合匹配。</p>
      </section>

      <section class="card">
        <h2 class="h2">你可能喜欢的工作方式</h2>
        <p class="para">{{ result.workStyleText }}</p>
      </section>

      <section class="card">
        <h2 class="h2">你可能不适合的工作环境</h2>
        <p class="para">{{ result.unsuitableText }}</p>
      </section>

      <section class="card">
        <h2 class="h2">推荐职业 Top 5</h2>
        <ul class="rec-list">
          <li v-for="(r, i) in result.recommendations" :key="r.id" class="rec-item">
            <div class="rec-rank">{{ i + 1 }}</div>
            <div class="rec-body">
              <h3 class="rec-title">{{ r.name }}</h3>
              <p class="rec-reason"><strong>推荐原因：</strong>{{ r.recommendReason }}</p>
              <p class="rec-ai"><strong>AI 时代变化：</strong>{{ r.aiEraChange }}</p>
              <RouterLink class="rec-link btn-gradient" :to="`/career/${r.careerId}`">查看详情</RouterLink>
            </div>
          </li>
        </ul>
      </section>

      <div class="footer-actions">
        <button type="button" class="btn-outline-block" @click="restart">重新测试</button>
        <RouterLink class="btn-outline-block" to="/career-library">进入职业观察库</RouterLink>
      </div>
    </template>
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
  padding: 20px 18px;
  margin: 0 12px 14px;
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
}

.intro .h1 {
  font-size: 20px;
  font-weight: 800;
  margin: 0 0 8px;
  color: var(--text);
}

.kicker {
  margin: 0 0 8px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #6366f1;
}

.sub {
  margin: 0;
  font-size: 14px;
  line-height: 1.65;
  color: var(--text-muted);
}

.quiz-card .q-title {
  font-size: 17px;
  font-weight: 700;
  margin: 18px 0 14px;
  line-height: 1.45;
  color: var(--text);
}

.progress-row {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-text {
  font-size: 13px;
  font-weight: 700;
  color: #5b21b6;
  min-width: 52px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.12);
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #6366f1, #a855f7);
  transition: width 0.25s ease;
}

.options {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.option {
  display: flex;
  gap: 12px;
  align-items: flex-start;
  text-align: left;
  width: 100%;
  padding: 14px 14px;
  border-radius: 14px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(255, 255, 255, 0.9);
  cursor: pointer;
  font: inherit;
  color: var(--text);
  transition:
    border-color var(--transition),
    box-shadow var(--transition),
    background var(--transition);
}

.option:hover {
  border-color: rgba(99, 102, 241, 0.35);
  box-shadow: 0 4px 16px rgba(99, 102, 241, 0.08);
}

.option.selected {
  border-color: rgba(99, 102, 241, 0.55);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.08), rgba(168, 85, 247, 0.06));
  box-shadow: 0 0 0 1px rgba(99, 102, 241, 0.12);
}

.option-idx {
  flex-shrink: 0;
  width: 26px;
  height: 26px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 8px;
  font-size: 12px;
  font-weight: 800;
  color: #5b21b6;
  background: rgba(99, 102, 241, 0.12);
}

.option-label {
  font-size: 14px;
  line-height: 1.55;
}

.nav-row {
  display: flex;
  justify-content: space-between;
  gap: 12px;
  margin-top: 22px;
  flex-wrap: wrap;
}

.btn-ghost {
  padding: 12px 18px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.45);
  background: rgba(255, 255, 255, 0.8);
  font-size: 15px;
  font-weight: 600;
  color: var(--text);
  cursor: pointer;
  transition: opacity var(--transition);
}

.btn-ghost:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.btn-primary {
  padding: 12px 20px;
  border-radius: 12px;
  border: none;
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  cursor: pointer;
}

.btn-primary:disabled {
  opacity: 0.45;
  cursor: not-allowed;
}

.result-hero .h1 {
  font-size: 22px;
  font-weight: 800;
  margin: 0 0 8px;
  color: var(--text);
}

.h2 {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 10px;
  color: var(--text);
}

.h2.mt {
  margin-top: 18px;
}

.score-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.score-row {
  display: grid;
  grid-template-columns: 100px 1fr 36px;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.score-row:last-child {
  margin-bottom: 0;
}

.score-name {
  font-size: 13px;
  color: var(--text-muted);
}

.score-bar-wrap {
  height: 8px;
  border-radius: 999px;
  background: rgba(99, 102, 241, 0.1);
  overflow: hidden;
}

.score-bar {
  height: 100%;
  border-radius: 999px;
  background: linear-gradient(90deg, #6366f1, #a855f7);
}

.score-num {
  font-size: 13px;
  font-weight: 700;
  text-align: right;
  color: var(--text);
}

.highlight {
  background: linear-gradient(135deg, rgba(238, 242, 255, 0.95), rgba(250, 245, 255, 0.9));
}

.lead {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: #4338ca;
}

.blend-note {
  margin: 14px 0 0;
  font-size: 13px;
  color: var(--text-muted);
}

.para {
  margin: 0;
  font-size: 14px;
  line-height: 1.7;
  color: var(--text);
}

.rec-list {
  list-style: none;
  margin: 0;
  padding: 0;
}

.rec-item {
  display: flex;
  gap: 14px;
  padding: 16px 0;
  border-top: 1px solid rgba(148, 163, 184, 0.2);
}

.rec-item:first-child {
  border-top: none;
  padding-top: 0;
}

.rec-rank {
  flex-shrink: 0;
  width: 32px;
  height: 32px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 800;
  font-size: 14px;
  color: #5b21b6;
  background: rgba(99, 102, 241, 0.12);
}

.rec-title {
  margin: 0 0 8px;
  font-size: 17px;
  font-weight: 700;
  color: var(--text);
}

.rec-reason,
.rec-ai {
  margin: 0 0 8px;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-muted);
}

.rec-link {
  display: inline-block;
  margin-top: 4px;
  padding: 10px 16px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  color: #fff;
}

.footer-actions {
  margin: 8px 12px 0;
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.btn-outline-block {
  display: block;
  padding: 13px 18px;
  text-align: center;
  border-radius: 14px;
  font-size: 15px;
  font-weight: 600;
  text-decoration: none;
  color: #5b21b6;
  background: rgba(255, 255, 255, 0.9);
  border: 1px solid rgba(99, 102, 241, 0.28);
  cursor: pointer;
  font: inherit;
  transition: transform var(--transition);
}

.btn-outline-block:hover {
  transform: translateY(-1px);
}
</style>
