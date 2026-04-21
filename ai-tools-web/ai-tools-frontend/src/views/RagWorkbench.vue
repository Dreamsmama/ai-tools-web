<script setup>
import { RouterLink } from 'vue-router'
</script>

<template>
  <div class="page">
    <header class="nav">
      <RouterLink class="back" to="/">← 首页</RouterLink>
    </header>

    <section class="card">
      <h1 class="title">RAG 使用模式</h1>
      <p class="sub">为避免操作冲突，已拆分为两个独立页面，请按场景选择。</p>
    </section>

    <RouterLink class="mode-card" to="/rag/upload">
      <h2 class="mode-title">模式 A：上传文档后提问</h2>
      <p class="mode-desc">适合个性化内容。可创建知识库、上传文件、入库后提问。</p>
    </RouterLink>

    <RouterLink class="mode-card" to="/rag/official">
      <h2 class="mode-title">模式 B：官方模板直接提问</h2>
      <p class="mode-desc">适合快速使用。无需上传文档，直接选择官方模板问答。</p>
    </RouterLink>
  </div>
</template>

<style scoped>
.page { max-width: 760px; margin: 0 auto; padding: 16px 12px 40px; min-height: 100vh; }
.nav { padding: 4px 4px 14px; }
.back { font-size: 14px; font-weight: 500; color: #6366f1; text-decoration: none; }
.card { background: rgba(255,255,255,.9); border-radius: 18px; padding: 18px 16px; margin-bottom: 14px; border: 1px solid rgba(148,163,184,.22); box-shadow: 0 4px 24px rgba(15,23,42,.06); }
.title { font-size: 21px; font-weight: 800; margin: 0 0 8px; }
.sub { margin: 0; color: #64748b; font-size: 14px; }
.mode-card {
  display: block;
  text-decoration: none;
  background: rgba(255,255,255,.9);
  border-radius: 18px;
  padding: 18px 16px;
  margin-bottom: 14px;
  border: 1px solid rgba(148,163,184,.22);
  box-shadow: 0 4px 24px rgba(15,23,42,.06);
}
.mode-title { margin: 0 0 8px; color: #0f172a; font-size: 18px; }
.mode-desc { margin: 0; color: #64748b; font-size: 14px; line-height: 1.6; }
</style>
