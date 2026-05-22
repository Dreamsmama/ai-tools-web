<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  slot: { type: Object, required: true },
  generating: { type: Boolean, default: false },
  busyId: { type: String, default: '' },
})

const emit = defineEmits(['generate', 'edit', 'delete', 'activate', 'deleteIp', 'preview', 'upload'])

/** 本次生成用的可选描述（不写入职业档案，仅当次生效） */
const generatePrompt = ref('')

watch(
  () => props.slot.role,
  () => {
    generatePrompt.value = ''
  },
)

function onGenerateClick() {
  emit('generate', props.slot, generatePrompt.value.trim())
}

const statusText = computed(() => {
  if (props.slot.isCurrent) return '已配置'
  if (props.slot.status === 'pending') return '待确认'
  return '未配置'
})

const statusClass = computed(() => {
  if (props.slot.isCurrent) return 'status--ok'
  if (props.slot.status === 'pending') return 'status--pending'
  return 'status--empty'
})

const promptPlaceholder = computed(() => {
  const hint = [props.slot.styleHint, props.slot.description].filter(Boolean).join('，')
  if (hint) return `留空则使用职业默认：${hint.slice(0, 48)}${hint.length > 48 ? '…' : ''}`
  return '如：35岁男性架构师，墨绿风衣，成熟稳重（留空则按职业生成；系统会先参考其他角色图再差异化）'
})
</script>

<template>
  <article
    class="role-card card"
    :class="{ 'role-card--current': slot.isCurrent, 'role-card--generating': generating }"
  >
    <div class="role-card__main">
      <button
        type="button"
        class="preview"
        :class="{ 'preview--empty': !slot.avatar }"
        @click="slot.avatar && emit('preview', slot.avatar, slot.profession)"
      >
        <img
          v-if="slot.avatar"
          :src="slot.avatar"
          :alt="slot.profession"
          class="preview-img"
          loading="lazy"
        />
        <div v-else class="preview-empty">
          <span v-if="generating" class="loading-ring" />
          <p v-if="generating">AI 生成中…</p>
          <template v-else>
            <span class="preview-icon">◎</span>
            <p>未设定角色</p>
          </template>
        </div>
        <span v-if="slot.avatar" class="zoom-hint">放大</span>
      </button>

      <div class="role-card__body">
        <div class="role-head">
          <div class="role-head__text">
            <h3 class="role-name">{{ slot.profession }}</h3>
            <p v-if="slot.description" class="role-desc">{{ slot.description }}</p>
          </div>
          <span class="status" :class="statusClass">{{ statusText }}</span>
        </div>

        <p v-if="slot.isCurrent" class="meta-line">
          <span class="meta-label">状态</span>
          <span class="meta-value">当前生效</span>
        </p>

        <label class="prompt-field">
          <span class="prompt-label">生成描述 <span class="optional">（可选）</span></span>
          <textarea
            v-model="generatePrompt"
            class="prompt-input"
            rows="2"
            maxlength="500"
            :disabled="generating"
            :placeholder="promptPlaceholder"
          />
        </label>

        <div class="actions">
          <button type="button" class="btn btn-ai" :disabled="generating" @click="onGenerateClick">
            {{ generating ? '生成中…' : '生成角色' }}
          </button>
          <button type="button" class="btn" :disabled="generating" @click="emit('upload', slot)">上传</button>
          <button type="button" class="btn btn-outline" @click="emit('edit', slot)">编辑职业</button>
          <button
            v-if="!slot.builtIn"
            type="button"
            class="btn btn-outline btn-danger"
            @click="emit('delete', slot)"
          >
            删除职业
          </button>
          <button
            v-if="slot.active"
            type="button"
            class="btn btn-outline btn-ghost"
            :disabled="!!busyId"
            @click="emit('deleteIp', slot.active.id)"
          >
            删除当前角色
          </button>
        </div>
      </div>
    </div>

    <section v-if="slot.pending?.length" class="pending">
      <h4 class="pending-title">待确认角色</h4>
      <ul class="pending-list">
        <li v-for="item in slot.pending" :key="item.id" class="pending-item">
          <button
            type="button"
            class="pending-thumb-btn"
            @click="emit('preview', item.baseImageUrl, item.name)"
          >
            <img :src="item.baseImageUrl" :alt="item.name" class="pending-thumb" loading="lazy" />
          </button>
          <p class="pending-name">{{ item.name }}</p>
          <div class="pending-actions">
            <button
              type="button"
              class="btn-sm btn-primary"
              :disabled="!!busyId"
              @click="emit('activate', item.id)"
            >
              {{ busyId === item.id ? '设置中…' : '设为当前' }}
            </button>
            <button
              type="button"
              class="btn-sm btn-ghost"
              :disabled="!!busyId"
              @click="emit('deleteIp', item.id)"
            >
              删除
            </button>
          </div>
        </li>
      </ul>
    </section>
  </article>
</template>

<style scoped>
.card {
  background: var(--surface-solid);
  border-radius: var(--radius);
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
}

.role-card {
  padding: 14px 16px;
  transition:
    box-shadow 0.2s,
    transform 0.2s;
}

.role-card:hover {
  transform: translateY(-1px);
  box-shadow:
    var(--shadow-card),
    0 6px 20px rgba(99, 102, 241, 0.1);
}

.role-card--current {
  box-shadow:
    var(--shadow-card),
    inset 0 0 0 2px rgba(99, 102, 241, 0.3);
}

.role-card--generating {
  opacity: 0.94;
}

.role-card__main {
  display: flex;
  gap: 16px;
  align-items: stretch;
}

.preview {
  flex: 0 0 auto;
  width: 132px;
  aspect-ratio: 3 / 4;
  position: relative;
  border: none;
  padding: 0;
  border-radius: 12px;
  overflow: hidden;
  background: linear-gradient(145deg, #0f172a, #1e293b);
  cursor: zoom-in;
}

.preview--empty {
  cursor: default;
}

.preview-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  object-position: top center;
  display: block;
}

.preview-empty {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 6px;
  color: rgba(255, 255, 255, 0.55);
  font-size: 12px;
  text-align: center;
  padding: 8px;
}

.preview-icon {
  font-size: 22px;
  opacity: 0.5;
}

.loading-ring {
  width: 24px;
  height: 24px;
  border: 3px solid rgba(255, 255, 255, 0.2);
  border-top-color: #a855f7;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.zoom-hint {
  position: absolute;
  right: 6px;
  bottom: 6px;
  padding: 3px 8px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 600;
  color: #fff;
  background: rgba(15, 23, 42, 0.7);
  pointer-events: none;
}

.role-card__body {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 10px;
}

.role-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
}

.role-head__text {
  min-width: 0;
}

.role-name {
  margin: 0 0 4px;
  font-size: 18px;
  font-weight: 800;
  line-height: 1.3;
}

.role-desc {
  margin: 0;
  font-size: 12px;
  line-height: 1.5;
  color: var(--text-muted);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.status {
  flex-shrink: 0;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 999px;
  white-space: nowrap;
}

.status--ok {
  color: #047857;
  background: rgba(16, 185, 129, 0.12);
}

.status--pending {
  color: #b45309;
  background: rgba(245, 158, 11, 0.14);
}

.status--empty {
  color: var(--text-muted);
  background: rgba(148, 163, 184, 0.15);
}

.meta-line {
  margin: 0;
  font-size: 12px;
}

.meta-label {
  color: var(--text-muted);
  margin-right: 6px;
}

.meta-value {
  font-weight: 600;
}

.prompt-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.prompt-label {
  font-size: 12px;
  font-weight: 700;
  color: #475569;
}

.prompt-label .optional {
  font-weight: 500;
  color: var(--text-muted);
}

.prompt-input {
  width: 100%;
  box-sizing: border-box;
  padding: 8px 10px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.45);
  font-size: 13px;
  line-height: 1.5;
  font-family: inherit;
  resize: vertical;
  min-height: 52px;
  background: #fafafa;
}

.prompt-input:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.55);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  background: #fff;
}

.prompt-input:disabled {
  opacity: 0.65;
}

.actions {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.btn {
  padding: 8px 14px;
  border-radius: 10px;
  border: 1px solid rgba(99, 102, 241, 0.35);
  background: #fff;
  font-size: 13px;
  font-weight: 600;
  color: #4f46e5;
  cursor: pointer;
  white-space: nowrap;
}

.btn-ai {
  background: linear-gradient(135deg, #6366f1, #a855f7);
  color: #fff;
  border: none;
}

.btn-outline {
  color: var(--text);
  border-color: rgba(148, 163, 184, 0.4);
}

.btn-ghost {
  color: var(--text-muted);
  background: transparent;
}

.btn-danger {
  color: #b91c1c;
  border-color: rgba(239, 68, 68, 0.35);
}

.btn:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

.pending {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px dashed rgba(148, 163, 184, 0.35);
}

.pending-title {
  margin: 0 0 10px;
  font-size: 12px;
  font-weight: 700;
  color: #b45309;
  letter-spacing: 0.02em;
}

.pending-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.pending-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  border-radius: 12px;
  background: rgba(245, 158, 11, 0.07);
  border: 1px solid rgba(245, 158, 11, 0.2);
  min-width: 0;
  max-width: 100%;
}

.pending-thumb-btn {
  flex-shrink: 0;
  padding: 0;
  border: none;
  background: none;
  cursor: zoom-in;
  border-radius: 6px;
  overflow: hidden;
}

.pending-thumb {
  width: 44px;
  height: 58px;
  object-fit: cover;
  display: block;
}

.pending-name {
  margin: 0;
  font-size: 12px;
  font-weight: 700;
  flex: 1;
  min-width: 72px;
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.pending-actions {
  display: flex;
  gap: 6px;
  flex-shrink: 0;
}

.btn-sm {
  padding: 6px 10px;
  font-size: 12px;
  font-weight: 600;
  border-radius: 8px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: #fff;
  cursor: pointer;
  white-space: nowrap;
}

.btn-primary {
  background: #6366f1;
  color: #fff;
  border: none;
}

.btn-ghost {
  background: transparent;
  color: var(--text-muted);
  border-color: transparent;
}

@media (max-width: 520px) {
  .role-card__main {
    flex-direction: column;
    align-items: center;
  }

  .preview {
    width: 100%;
    max-width: 200px;
    aspect-ratio: 3 / 4;
  }

  .role-card__body {
    width: 100%;
  }

  .role-head {
    flex-direction: column;
    align-items: flex-start;
  }

  .actions {
    justify-content: flex-start;
  }

  .pending-item {
    flex-wrap: wrap;
    width: 100%;
  }

  .pending-name {
    max-width: none;
    flex-basis: 100%;
  }
}
</style>
