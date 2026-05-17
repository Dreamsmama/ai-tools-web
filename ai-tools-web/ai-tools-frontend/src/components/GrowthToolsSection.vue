<script setup>
import { RouterLink } from 'vue-router'

const tools = [
  {
    to: '/summary',
    title: '职场沟通回复助手',
    tag: '沟通',
    desc: '识别沟通意图、情绪与风险，生成更专业、更有边界感的回复建议。',
  },
  {
    to: '/medical',
    title: '就医前沟通准备',
    tag: '辅助',
    desc: '整理症状/检查/疑问，用好和医生的 10 分钟',
  },
  {
    to: '/rag',
    title: 'RAG 知识库问答',
    tag: '知识',
    desc: '上传文档，建立知识库，基于引用做问答',
  },
  {
    to: '/model-compare',
    title: '模型优化实验 / 微调效果对比',
    tag: '实验',
    desc: '同一输入下对比原始模型与优化模型输出差异',
  },
]
</script>

<template>
  <section class="growth-section" aria-labelledby="growth-section-title">
    <header class="growth-head">
      <p class="growth-kicker">职场工具</p>
      <h2 id="growth-section-title" class="growth-title">更多 AI 职场成长工具</h2>
      <p class="growth-sub">
        当你遇到沟通、选择、表达和整理问题时，用 AI 帮你快速理清。
      </p>
    </header>

    <div class="growth-grid">
      <RouterLink
        v-for="tool in tools"
        :key="tool.to"
        class="growth-card-link"
        :to="tool.to"
      >
        <div class="growth-card">
          <div class="growth-accent" aria-hidden="true" />
          <div class="growth-row">
            <span class="growth-card-title">{{ tool.title }}</span>
            <span class="growth-tag">{{ tool.tag }}</span>
          </div>
          <p class="growth-desc">{{ tool.desc }}</p>
        </div>
      </RouterLink>
    </div>
  </section>
</template>

<style scoped>
.growth-section {
  margin: 0 12px 28px;
}

.growth-head {
  margin-bottom: 16px;
  padding: 0 4px;
}

.growth-kicker {
  margin: 0 0 8px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #6366f1;
}

.growth-title {
  margin: 0 0 10px;
  font-size: 20px;
  font-weight: 800;
  line-height: 1.35;
  letter-spacing: -0.02em;
  color: var(--text);
}

.growth-sub {
  margin: 0;
  font-size: 14px;
  line-height: 1.65;
  color: var(--text-muted);
}

.growth-grid {
  display: grid;
  grid-template-columns: 1fr;
  gap: 10px;
}

@media (min-width: 640px) {
  .growth-grid {
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
}

.growth-card-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

.growth-card {
  position: relative;
  overflow: hidden;
  padding: 16px 16px 16px 20px;
  border-radius: var(--radius-sm);
  background: var(--surface-solid);
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
  transition:
    transform var(--transition),
    box-shadow var(--transition);
}

.growth-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-float);
}

.growth-accent {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 3px;
  background: linear-gradient(180deg, #6366f1, #a855f7);
  border-radius: 3px 0 0 3px;
  opacity: 0.7;
}

.growth-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px;
}

.growth-card-title {
  font-size: 15px;
  font-weight: 700;
  color: var(--text);
  line-height: 1.35;
}

.growth-tag {
  flex-shrink: 0;
  font-size: 10px;
  font-weight: 600;
  padding: 4px 9px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.08));
  color: #5b21b6;
  border: 1px solid rgba(99, 102, 241, 0.18);
}

.growth-desc {
  margin: 10px 0 0;
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.55;
}
</style>
