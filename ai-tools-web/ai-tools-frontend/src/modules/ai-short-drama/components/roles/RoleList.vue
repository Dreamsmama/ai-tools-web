<script setup>
import RoleCard from './RoleCard.vue'

defineProps({
  roles: { type: Array, default: () => [] },
  loading: { type: Boolean, default: false },
  loadError: { type: String, default: '' },
  generatingRole: { type: String, default: '' },
  busyId: { type: String, default: '' },
})

const emit = defineEmits([
  'generate',
  'edit',
  'delete',
  'activate',
  'deleteIp',
  'preview',
  'upload',
])
</script>

<template>
  <div v-if="loading && !roles.length" class="hint card">加载角色库…</div>

  <div v-else-if="loadError && !roles.length" class="empty card empty--error">
    <p class="empty-text">{{ loadError }}</p>
    <p class="empty-hint">请确认后端已启动：http://127.0.0.1:8000/health</p>
  </div>

  <div v-else-if="!roles.length" class="empty card">
    <p class="empty-text">还没有职业角色，点击「新增职业」开始创建。</p>
  </div>

  <div v-else class="grid">
    <RoleCard
      v-for="slot in roles"
      :key="slot.id"
      :slot="slot"
      :generating="generatingRole === slot.role"
      :busy-id="busyId"
      @generate="(slot, prompt) => emit('generate', slot, prompt)"
      @edit="emit('edit', $event)"
      @delete="emit('delete', $event)"
      @activate="emit('activate', $event)"
      @delete-ip="emit('deleteIp', $event)"
      @preview="(url, title) => emit('preview', url, title)"
      @upload="emit('upload', $event)"
    />
  </div>
</template>

<style scoped>
.card {
  background: var(--surface-solid);
  border-radius: var(--radius);
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
}

.hint,
.empty {
  padding: 32px 20px;
  text-align: center;
}

.empty-text {
  margin: 0;
  font-size: 14px;
  color: var(--text-muted);
  line-height: 1.6;
}

.grid {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
