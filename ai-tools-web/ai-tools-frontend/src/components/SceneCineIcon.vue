<script setup>
/** @type {{ name: string }} */
defineProps({
  name: { type: String, default: 'default' },
})
</script>

<template>
  <svg
    class="scene-cine-icon"
    viewBox="0 0 48 48"
    fill="none"
    xmlns="http://www.w3.org/2000/svg"
    aria-hidden="true"
  >
    <!-- 群聊告警：工作群炸了 -->
    <g v-if="name === 'alert'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M8 28h6l2 4 2-4h4a4 4 0 0 0 4-4V16a4 4 0 0 0-4-4H12a4 4 0 0 0-4 4v8a4 4 0 0 0 4 4Z" />
      <path d="M14 18v4M18 18v4" opacity="0.85" />
      <path d="M28 10h5l1.5 3 1.5-3h3.5a3 3 0 0 1 3 3v5a3 3 0 0 1-3 3h-5" />
      <path d="M32 14v2" />
      <circle cx="36" cy="8" r="5" fill="#fca5a5" stroke="#fecaca" />
      <path d="M36 6v4M34 8h4" stroke="#7f1d1d" stroke-width="1.8" />
    </g>

    <!-- 会议 / 面试 -->
    <g v-else-if="name === 'meeting'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <rect x="6" y="22" width="36" height="14" rx="3" />
      <path d="M14 22v-4a10 10 0 0 1 20 0v4" />
      <circle cx="16" cy="12" r="4" />
      <circle cx="32" cy="12" r="4" />
      <path d="M18 29h12" opacity="0.7" />
    </g>

    <!-- 工单 / 混乱 -->
    <g v-else-if="name === 'chaos'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M12 8h18l6 8v22a2 2 0 0 1-2 2H12a2 2 0 0 1-2-2V10a2 2 0 0 1 2-2Z" />
      <path d="M30 8v8h8" />
      <path d="M16 22h16M16 28h12M16 34h8" opacity="0.75" />
      <circle cx="34" cy="14" r="6" fill="#f87171" stroke="#fecaca" />
      <path d="M34 11v6M31 14h6" stroke="#7f1d1d" stroke-width="1.8" />
    </g>

    <!-- 深夜工位 -->
    <g v-else-if="name === 'night'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M10 14a11 11 0 1 0 14 0 11 11 0 0 0-14 0Z" />
      <path d="M17 8v12" opacity="0.35" />
      <rect x="24" y="24" width="18" height="12" rx="2" />
      <path d="M24 36h18" />
    </g>

    <!-- 生活 / 下班 -->
    <g v-else-if="name === 'life'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <rect x="14" y="8" width="20" height="32" rx="4" />
      <path d="M20 12h8" opacity="0.6" />
      <circle cx="24" cy="34" r="2" fill="currentColor" stroke="none" />
      <path d="M6 18l3 3M6 24l4-1M6 30l3-2" opacity="0.8" />
    </g>

    <!-- 招聘收件箱 -->
    <g v-else-if="name === 'inbox'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <path d="M6 16h36l-4 20H10L6 16Z" />
      <path d="M6 16l10 8 10-8 10 8" />
      <path d="M18 24h12M18 30h8" opacity="0.75" />
    </g>

    <!-- 情绪 / 沟通 -->
    <g v-else-if="name === 'emotion'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <circle cx="24" cy="22" r="12" />
      <circle cx="19" cy="20" r="1.5" fill="currentColor" stroke="none" />
      <circle cx="29" cy="20" r="1.5" fill="currentColor" stroke="none" />
      <path d="M18 28c2-3 10-3 12 0" />
      <path d="M8 12l4 2M40 12l-4 2M8 36l5-3M40 36l-5-3" opacity="0.65" />
    </g>

    <!-- 保密 / 压力 -->
    <g v-else-if="name === 'pressure'" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <rect x="10" y="18" width="28" height="22" rx="3" />
      <path d="M16 18v-4a8 8 0 0 1 16 0v4" />
      <circle cx="24" cy="28" r="3" />
      <path d="M24 31v4" />
      <path d="M8 12h10M30 12h10" opacity="0.55" />
    </g>

    <!-- 默认工位 -->
    <g v-else stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
      <rect x="8" y="14" width="32" height="22" rx="3" />
      <path d="M8 34h32" />
      <path d="M24 34v6" />
      <path d="M18 40h12" />
    </g>
  </svg>
</template>

<style scoped>
.scene-cine-icon {
  display: block;
  width: 52px;
  height: 52px;
  color: rgba(248, 250, 252, 0.95);
  filter: drop-shadow(0 2px 10px rgba(0, 0, 0, 0.35));
}
</style>
