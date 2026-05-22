<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import { useProfessionRoles } from '../composables/useProfessionRoles.js'
import AddRoleDialog from './roles/AddRoleDialog.vue'
import RoleList from './roles/RoleList.vue'

const emit = defineEmits(['toast', 'error'])

const {
  loading,
  actionId,
  generatingRole,
  loadError,
  roles,
  loadRoles,
  addProfession,
  editProfession,
  removeProfession,
  generateRole,
  setCurrentRole,
  removeCharacterIp,
  uploadBaseImage,
} = useProfessionRoles()

const dialogOpen = ref(false)
const dialogMode = ref('create')
const dialogSaving = ref(false)
const editTarget = ref(null)
const fileInput = ref(null)
const uploadRoleKey = ref('')

/** @type {import('vue').Ref<{ url: string, title: string } | null>} */
const preview = ref(null)

onMounted(() => {
  window.addEventListener('keydown', onPreviewKeydown)
  loadRoles().then((res) => {
    if (res && !res.ok) emit('error', res.message)
  })
})

onUnmounted(() => {
  window.removeEventListener('keydown', onPreviewKeydown)
})

function onPreviewKeydown(e) {
  if (e.key === 'Escape') preview.value = null
}

function openCreate() {
  editTarget.value = null
  dialogMode.value = 'create'
  dialogOpen.value = true
}

function openEdit(slot) {
  editTarget.value = slot
  dialogMode.value = 'edit'
  dialogOpen.value = true
}

async function onDialogSubmit(payload) {
  dialogSaving.value = true
  try {
    if (dialogMode.value === 'edit' && editTarget.value?.professionId) {
      const res = await editProfession(editTarget.value.professionId, payload)
      if (!res.ok) {
        emit('error', res.message)
        return
      }
      emit('toast', '职业已更新')
    } else {
      const res = await addProfession(payload)
      if (!res.ok) {
        emit('error', res.message)
        return
      }
      emit('toast', '职业已创建，可生成角色 IP')
    }
    dialogOpen.value = false
  } finally {
    dialogSaving.value = false
  }
}

async function onGenerate(slot, extraPrompt = '') {
  const res = await generateRole(slot, extraPrompt)
  if (!res.ok) {
    emit('error', res.message)
    return
  }
  emit('toast', `已生成 ${res.data?.length || 0} 个候选角色，请确认后设为当前`)
}

async function onDelete(slot) {
  if (!window.confirm(`确认删除职业「${slot.profession}」吗？\n将同时删除该职业下所有角色图片。`)) {
    return
  }
  const res = await removeProfession(slot.professionId)
  if (!res.ok) {
    emit('error', res.message)
    return
  }
  emit('toast', '职业已删除')
}

async function onActivate(ipId) {
  const res = await setCurrentRole(ipId)
  if (!res.ok) {
    emit('error', res.message)
    return
  }
  emit('toast', '已设为当前基础角色')
}

async function onDeleteIp(ipId) {
  if (!window.confirm('确认删除该角色候选？')) return
  const res = await removeCharacterIp(ipId)
  if (!res.ok) {
    emit('error', res.message)
    return
  }
  emit('toast', '已删除')
}

function onUpload(slot) {
  uploadRoleKey.value = slot.role
  fileInput.value?.click()
}

async function onFileChange(e) {
  const file = e.target.files?.[0]
  e.target.value = ''
  if (!file || !uploadRoleKey.value) return
  const res = await uploadBaseImage(file, uploadRoleKey.value)
  if (!res.ok) {
    emit('error', res.message)
    return
  }
  emit('toast', '已上传，请确认后设为当前角色')
}
</script>

<template>
  <section class="workbench">
    <header class="hero card">
      <div class="hero-row">
        <div>
          <p class="kicker">Character IP</p>
          <h2 class="title">角色 IP 工作台</h2>
          <p class="sub">
            每个职业一张<strong>已确认</strong>的基础角色图，成片人物镜头将固定使用该 IP。
          </p>
        </div>
        <button type="button" class="btn-add" @click="openCreate">+ 新增职业</button>
      </div>
      <p class="rule">AI 生成的角色默认为「待确认」，需手动「设为当前角色」后才会进入成片。</p>
    </header>

    <p v-if="loadError" class="load-error card">{{ loadError }}</p>

    <RoleList
      :roles="roles"
      :loading="loading"
      :load-error="loadError"
      :generating-role="generatingRole"
      :busy-id="actionId"
      @generate="onGenerate"
      @edit="openEdit"
      @delete="onDelete"
      @activate="onActivate"
      @delete-ip="onDeleteIp"
      @preview="(url, title) => (preview = { url, title })"
      @upload="onUpload"
    />

    <AddRoleDialog
      :open="dialogOpen"
      :mode="dialogMode"
      :initial="editTarget || {}"
      :saving="dialogSaving"
      @close="dialogOpen = false"
      @submit="onDialogSubmit"
    />

    <input
      ref="fileInput"
      type="file"
      accept="image/png,image/jpeg,image/webp"
      class="sr-only"
      @change="onFileChange"
    />

    <Teleport to="body">
      <div
        v-if="preview"
        class="lightbox"
        role="dialog"
        aria-modal="true"
        @click.self="preview = null"
      >
        <div class="lightbox-panel">
          <header class="lightbox-head">
            <p class="lightbox-title">{{ preview.title }}</p>
            <button type="button" class="lightbox-close" @click="preview = null">✕</button>
          </header>
          <img :src="preview.url" :alt="preview.title" class="lightbox-img" />
        </div>
      </div>
    </Teleport>
  </section>
</template>

<style scoped>
.workbench {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.card {
  background: var(--surface-solid);
  border-radius: var(--radius);
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
}

.hero {
  padding: 18px 16px;
  background: linear-gradient(145deg, rgba(99, 102, 241, 0.08), rgba(168, 85, 247, 0.05));
}

.hero-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 8px;
}

.kicker {
  margin: 0 0 6px;
  font-size: 11px;
  font-weight: 700;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: #6366f1;
}

.title {
  margin: 0 0 6px;
  font-size: 20px;
  font-weight: 800;
}

.sub {
  margin: 0;
  font-size: 13px;
  line-height: 1.55;
  color: var(--text-muted);
}

.rule {
  margin: 0;
  font-size: 12px;
  color: #7c3aed;
}

.btn-add {
  flex-shrink: 0;
  padding: 10px 16px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 700;
  color: #fff;
  cursor: pointer;
  background: linear-gradient(135deg, #6366f1, #a855f7);
  box-shadow: 0 4px 14px rgba(99, 102, 241, 0.35);
  transition: transform 0.15s;
}

.btn-add:hover {
  transform: translateY(-1px);
}

.load-error {
  padding: 12px 14px;
  margin-bottom: 0;
  font-size: 13px;
  line-height: 1.5;
  color: #b45309;
  background: rgba(245, 158, 11, 0.1);
  border: 1px solid rgba(245, 158, 11, 0.35);
}

.empty--error .empty-text {
  color: #b91c1c;
  font-weight: 600;
}

.empty-hint {
  margin: 8px 0 0;
  font-size: 12px;
  color: var(--text-muted);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
}

.lightbox {
  position: fixed;
  inset: 0;
  z-index: 3000;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 16px;
  background: rgba(15, 23, 42, 0.88);
}

.lightbox-panel {
  width: min(420px, 100%);
  background: #fff;
  border-radius: 16px;
  overflow: hidden;
}

.lightbox-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 14px;
}

.lightbox-title {
  margin: 0;
  font-weight: 700;
}

.lightbox-close {
  border: none;
  background: #f1f5f9;
  border-radius: 8px;
  width: 32px;
  height: 32px;
  cursor: pointer;
}

.lightbox-img {
  width: 100%;
  display: block;
  background: #0f172a;
}
</style>
