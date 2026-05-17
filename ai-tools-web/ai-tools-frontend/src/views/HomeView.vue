<script setup>
import { RouterLink } from 'vue-router'
import CareerHeroSection from '../components/CareerHeroSection.vue'
import WorkerPersonalityLabSection from '../components/WorkerPersonalityLabSection.vue'
import GaokaoZoneSection from '../components/GaokaoZoneSection.vue'
</script>

<template>
  <div class="page">
    <div class="brand-badge">AI 工具台</div>

    <GaokaoZoneSection />

    <CareerHeroSection />

    <WorkerPersonalityLabSection />

    <div class="tools-section">
      <div class="section-title">
        <span class="section-dot" />场景工具
      </div>
      <RouterLink class="tool-card-link tool-card-link--interest" to="/tools/interest-explorer">
        <div class="tool-card tool-card--interest">
          <div class="tool-accent" aria-hidden="true" />
          <div class="tool-row">
            <span class="tool-title">AI 兴趣推荐 / 兴趣探索器</span>
            <span class="tool-tag tool-tag--mint">兴趣</span>
          </div>
          <p class="tool-desc">分析你的生活节奏与性格，找到真正适合长期坚持的爱好</p>
          <span class="tool-cta tool-cta--mint">AI 帮我找兴趣</span>
        </div>
      </RouterLink>
      <RouterLink class="tool-card-link tool-card-link--evening" to="/tools/evening-plan">
        <div class="tool-card tool-card--evening">
          <div class="tool-accent" aria-hidden="true" />
          <div class="tool-row">
            <span class="tool-title">下班后不知道干什么</span>
            <span class="tool-tag tool-tag--warm">生活</span>
          </div>
          <p class="tool-desc">测测你今晚适合吃什么、去哪玩、做什么</p>
          <span class="tool-cta">AI 帮我安排今晚</span>
        </div>
      </RouterLink>
      <RouterLink class="tool-card-link" to="/summary">
        <div class="tool-card">
          <div class="tool-accent" aria-hidden="true" />
          <div class="tool-row">
            <span class="tool-title">职场沟通回复助手</span>
            <span class="tool-tag">沟通</span>
          </div>
          <p class="tool-desc">
            识别沟通意图、情绪与风险，生成更专业、更有边界感的回复建议。
          </p>
        </div>
      </RouterLink>
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
      <RouterLink class="tool-card-link" to="/tools/memory-compare">
        <div class="tool-card">
          <div class="tool-accent" aria-hidden="true" />
          <div class="tool-row">
            <span class="tool-title">AI 记忆对比助手</span>
            <span class="tool-tag">对比</span>
          </div>
          <p class="tool-desc">对比无记忆回答与记忆增强回答，直观看出差异</p>
        </div>
      </RouterLink>
      <RouterLink class="tool-card-link" to="/tools/offer-decision">
        <div class="tool-card">
          <div class="tool-accent" aria-hidden="true" />
          <div class="tool-row">
            <span class="tool-title">Offer / 职业决策辅助</span>
            <span class="tool-tag">决策</span>
          </div>
          <p class="tool-desc">分析 offer 风险、成长、稳定性与长期发展</p>
        </div>
      </RouterLink>
      <RouterLink class="tool-card-link" to="/xiaohongshu-agent">
        <div class="tool-card">
          <div class="tool-accent" aria-hidden="true" />
          <div class="tool-row">
            <span class="tool-title">小红书内容生产 Agent</span>
            <span class="tool-tag">Agent</span>
          </div>
          <p class="tool-desc">输入主题/产品/人群，一键生成标题、文案、图片提示词</p>
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
  margin: 4px 4px 14px;
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

.tool-card--evening .tool-accent {
  background: linear-gradient(180deg, #f59e0b, #f97316, #fb7185);
}

.tool-tag--warm {
  background: linear-gradient(135deg, rgba(245, 158, 11, 0.15), rgba(251, 113, 133, 0.12));
  color: #c2410c;
  border-color: rgba(245, 158, 11, 0.28);
}

.tool-card--interest .tool-accent {
  background: linear-gradient(180deg, #10b981, #34d399, #6ee7b7);
}

.tool-tag--mint {
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(52, 211, 153, 0.12));
  color: #047857;
  border-color: rgba(16, 185, 129, 0.28);
}

.tool-cta {
  display: inline-block;
  margin-top: 14px;
  padding: 8px 14px;
  font-size: 13px;
  font-weight: 600;
  color: #fff;
  border-radius: 999px;
  background: linear-gradient(135deg, #f59e0b 0%, #f97316 55%, #fb7185 100%);
  box-shadow: 0 6px 18px rgba(249, 115, 22, 0.28);
}

.tool-cta--mint {
  background: linear-gradient(135deg, #10b981 0%, #34d399 55%, #6ee7b7 100%);
  box-shadow: 0 6px 18px rgba(16, 185, 129, 0.28);
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
