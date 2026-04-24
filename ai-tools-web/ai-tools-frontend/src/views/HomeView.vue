<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="page">
    <div class="brand-badge">AI 工具台</div>

    <section class="card hero">
      <div class="hero-glow" aria-hidden="true" />
      <h1 class="h1">
        <span class="gradient-text">把一堆聊天</span>，整理成你该记住的重点
      </h1>
      <p class="sub">
        输出：结论 · 待办 · 风险（适合工作/群聊/重要对话）
      </p>
    </section>

    <RouterLink class="btn-link btn-gradient" to="/summary">
      开始整理聊天
    </RouterLink>

    <section class="card card-glass">
      <h2 class="h2">它能帮你做什么？</h2>
      <p class="sub">
        1）提取核心结论　2）列出下一步待办　3）标出没说清/有风险的点
      </p>
    </section>

    <div class="tools-section">
      <div class="section-title">
        <span class="section-dot" />场景工具
      </div>
      <RouterLink class="tool-card-link" to="/medical">
        <div class="tool-card">
          <div class="tool-accent" aria-hidden="true" />
          <div class="tool-row">
            <span class="tool-title">就医前沟通准备</span>
            <span class="tool-tag">辅助</span>
          </div>
          <p class="tool-desc">整理症状/检查/疑问，用好和医生的 10 分钟</p>
        </div>
      </RouterLink>
      <RouterLink class="tool-card-link" to="/rag">
        <div class="tool-card">
          <div class="tool-accent" aria-hidden="true" />
          <div class="tool-row">
            <span class="tool-title">RAG 知识库问答</span>
            <span class="tool-tag">新</span>
          </div>
          <p class="tool-desc">上传文档，建立知识库，基于引用做问答</p>
        </div>
      </RouterLink>
      <RouterLink class="tool-card-link" to="/model-compare">
        <div class="tool-card">
          <div class="tool-accent" aria-hidden="true" />
          <div class="tool-row">
            <span class="tool-title">模型优化实验 / 微调效果对比</span>
            <span class="tool-tag">实验</span>
          </div>
          <p class="tool-desc">同一输入下对比原始模型与优化模型输出差异</p>
        </div>
      </RouterLink>
    </div>

    <p class="disclaimer">
      本工具仅用于就医前的信息整理与沟通准备，不提供医疗诊断或治疗建议。最终请以专业医生意见为准。
    </p>
  </div>
</template>

<style scoped>
.page {
  max-width: 720px;
  margin: 0 auto;
  padding: 24px 16px 40px;
  min-height: 100vh;
  position: relative;
}

.brand-badge {
  display: inline-block;
  margin: 0 12px 16px;
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 600;
  letter-spacing: 0.06em;
  text-transform: uppercase;
  color: #6366f1;
  background: rgba(99, 102, 241, 0.12);
  border: 1px solid rgba(99, 102, 241, 0.25);
  border-radius: 999px;
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

.hero {
  padding: 24px 20px;
}

.hero-glow {
  position: absolute;
  top: -40%;
  right: -20%;
  width: 70%;
  height: 120%;
  background: radial-gradient(
    circle,
    rgba(99, 102, 241, 0.18) 0%,
    transparent 65%
  );
  pointer-events: none;
}

.h1 {
  position: relative;
  font-size: 22px;
  font-weight: 800;
  margin: 0 0 10px;
  line-height: 1.35;
  letter-spacing: -0.02em;
  color: var(--text);
}

.gradient-text {
  background: linear-gradient(135deg, #6366f1, #8b5cf6, #a855f7);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.h2 {
  font-size: 16px;
  font-weight: 700;
  margin: 0 0 10px;
  color: var(--text);
}

.sub {
  position: relative;
  color: var(--text-muted);
  font-size: 14px;
  line-height: 1.65;
  margin: 0;
}

.card-glass {
  background: rgba(255, 255, 255, 0.78);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.btn-link {
  display: block;
  margin: 8px 24px 22px;
  padding: 14px 18px;
  text-align: center;
  border-radius: 14px;
  text-decoration: none;
  font-size: 16px;
  font-weight: 600;
}

.tools-section {
  margin: 8px 12px 0;
}

.section-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.04em;
  color: var(--text-muted);
  text-transform: uppercase;
  margin: 20px 4px 14px;
}

.section-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  box-shadow: 0 0 12px rgba(99, 102, 241, 0.5);
}

.tool-card-link {
  text-decoration: none;
  color: inherit;
  display: block;
}

.tool-card {
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

.tool-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-float);
}

.tool-accent {
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 4px;
  background: linear-gradient(180deg, #6366f1, #a855f7, #06b6d4);
  border-radius: 4px 0 0 4px;
}

.tool-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.tool-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--text);
}

.tool-tag {
  font-size: 11px;
  font-weight: 600;
  padding: 5px 11px;
  border-radius: 999px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(168, 85, 247, 0.1));
  color: #5b21b6;
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.tool-desc {
  margin: 12px 0 0;
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.55;
}

.disclaimer {
  margin: 24px 12px 0;
  padding: 14px 16px;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, rgba(254, 243, 199, 0.65), rgba(255, 237, 213, 0.5));
  color: #92400e;
  font-size: 12px;
  line-height: 1.65;
  border: 1px solid rgba(251, 191, 36, 0.35);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.5);
}
</style>
