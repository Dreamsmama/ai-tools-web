<script setup>
import { computed, ref, watch } from 'vue'

const props = defineProps({
  open: { type: Boolean, default: false },
  mode: { type: String, default: 'create' },
  initial: {
    type: Object,
    default: () => ({ name: '', description: '', styleHint: '' }),
  },
  saving: { type: Boolean, default: false },
})

const emit = defineEmits(['close', 'submit'])

const name = ref('')
const description = ref('')
const styleHint = ref('')

const title = computed(() => (props.mode === 'edit' ? '编辑职业' : '新增职业'))

watch(
  () => props.open,
  (v) => {
    if (!v) return
    name.value = props.initial?.name || props.initial?.profession || ''
    description.value = props.initial?.description || ''
    styleHint.value = props.initial?.styleHint || ''
  },
)

function onClose() {
  if (props.saving) return
  emit('close')
}

function onSubmit() {
  const label = name.value.trim()
  if (!label) return
  emit('submit', {
    name: label,
    description: description.value.trim(),
    styleHint: styleHint.value.trim(),
  })
}
</script>

<template>
  <Teleport to="body">
    <div v-if="open" class="dialog-backdrop" @click.self="onClose">
      <div class="dialog card" role="dialog" :aria-label="title">
        <header class="dialog-head">
          <h3 class="dialog-title">{{ title }}</h3>
          <button type="button" class="dialog-close" aria-label="关闭" @click="onClose">✕</button>
        </header>

        <form class="dialog-body" @submit.prevent="onSubmit">
          <label class="field">
            <span class="label">职业名称 <em>*</em></span>
            <input v-model="name" class="input" maxlength="24" placeholder="例如：教师、护士" required />
          </label>
          <label class="field">
            <span class="label">职业描述</span>
            <textarea
              v-model="description"
              class="input input--area"
              rows="3"
              maxlength="500"
              placeholder="工作场景、情绪基调等（可选）"
            />
          </label>
          <label class="field">
            <span class="label">默认角色风格</span>
            <textarea
              v-model="styleHint"
              class="input input--area"
              rows="2"
              maxlength="500"
              placeholder="例如：干练短发、白大褂、温和微笑（可选）"
            />
          </label>

          <footer class="dialog-foot">
            <button type="button" class="btn btn-ghost" :disabled="saving" @click="onClose">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="saving || !name.trim()">
              {{ saving ? '保存中…' : mode === 'edit' ? '保存' : '创建职业' }}
            </button>
          </footer>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.dialog-backdrop {
  position: fixed;
  inset: 0;
  z-index: 4000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background: rgba(15, 23, 42, 0.55);
  backdrop-filter: blur(4px);
}

.card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 24px 64px rgba(99, 102, 241, 0.18);
}

.dialog {
  width: min(420px, 100%);
  max-height: 90vh;
  overflow: auto;
}

.dialog-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 18px 0;
}

.dialog-title {
  margin: 0;
  font-size: 18px;
  font-weight: 800;
  color: #1e1b4b;
}

.dialog-close {
  width: 32px;
  height: 32px;
  border: none;
  border-radius: 8px;
  background: rgba(148, 163, 184, 0.15);
  cursor: pointer;
}

.dialog-body {
  padding: 14px 18px 18px;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label {
  font-size: 13px;
  font-weight: 700;
  color: #334155;
}

.label em {
  color: #ef4444;
  font-style: normal;
}

.input {
  width: 100%;
  box-sizing: border-box;
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.45);
  font-size: 14px;
  font-family: inherit;
}

.input--area {
  resize: vertical;
  min-height: 64px;
}

.input:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.55);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.dialog-foot {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
  margin-top: 4px;
}

.btn {
  padding: 10px 18px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  cursor: pointer;
  border: none;
}

.btn-ghost {
  background: transparent;
  color: #64748b;
  border: 1px solid rgba(148, 163, 184, 0.4);
}

.btn-primary {
  background: linear-gradient(135deg, #6366f1, #a855f7);
  color: #fff;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>
