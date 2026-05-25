<script setup>
import { RouterLink } from 'vue-router'

const scenarioTools = [
  {
    to: '/tools/life-rpg',
    title: 'AI 人生副本',
    tag: '成长',
    desc: '根据状态整理长期路线，生成今日可推进的安排',
  },
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
    tag: '新',
    desc: '上传文档，建立知识库，基于引用做问答',
  },
  {
    to: '/model-compare',
    title: '模型优化实验 / 微调效果对比',
    tag: '实验',
    desc: '同一输入下对比原始模型与优化模型输出差异',
  },
  {
    to: '/tools/memory-compare',
    title: 'AI 记忆对比助手',
    tag: '对比',
    desc: '对比无记忆回答与记忆增强回答，直观看出差异',
  },
  {
    to: '/tools/offer-decision',
    title: 'Offer / 职业决策辅助',
    tag: '决策',
    desc: '分析 offer 风险、成长、稳定性与长期发展',
  },
  {
    to: '/xiaohongshu-agent',
    title: '小红书内容生产 Agent',
    tag: 'Agent',
    desc: '输入主题/产品/人群，一键生成标题、文案、图片提示词',
  },
  {
    to: '/tools/ai-short-drama',
    title: 'AI 职业图文成片',
    tag: '图文',
    desc: '职业观察局风格：一句文案一张图，自动匹配素材，可合成竖屏成片视频',
  },
  {
    to: '/tools/hairstyle',
    title: 'AI 换发型',
    tag: '形象',
    desc: '上传自拍，AI 生成不同发型效果，看看哪种更适合你',
  },
]
</script>

<template>
  <div class="page">
    <div class="page-top">
      <RouterLink class="back-home" to="/">← 返回产品首页</RouterLink>
      <div class="brand-badge">AI 工具库</div>
      <p class="page-sub">场景化 AI 工具合集，按场景快速找到你需要的功能</p>
    </div>

    <div class="tools-section">
      <div class="section-title">
        <span class="section-dot" />场景工具
      </div>

      <RouterLink
        v-for="tool in scenarioTools"
        :key="tool.to"
        class="tool-card-link"
        :to="tool.to"
      >
        <div class="tool-card">
          <div class="tool-accent" aria-hidden="true" />
          <div class="tool-row">
            <span class="tool-title">{{ tool.title }}</span>
            <span class="tool-tag">{{ tool.tag }}</span>
          </div>
          <p class="tool-desc">{{ tool.desc }}</p>
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
}

.page-top {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 10px;
  margin: 0 12px 20px;
}

.back-home {
  font-size: 13px;
  font-weight: 600;
  color: #6366f1;
  text-decoration: none;
}

.back-home:hover {
  color: #4f46e5;
}

.brand-badge {
  display: inline-block;
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

.page-sub {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: var(--text-muted);
}

.tools-section {
  margin: 0 12px;
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
  margin-bottom: 10px;
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
  gap: 8px;
}

.tool-title {
  font-size: 17px;
  font-weight: 700;
  color: var(--text);
}

.tool-tag {
  flex-shrink: 0;
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
