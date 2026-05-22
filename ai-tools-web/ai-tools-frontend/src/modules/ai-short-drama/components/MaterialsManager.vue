<script setup>
import { computed, onMounted, ref } from 'vue'
import {
  MATERIAL_CATEGORY_TABS,
  MATERIAL_EMOTIONS,
  MATERIAL_ROLES,
  MATERIAL_ROLES_UPLOAD,
  MATERIAL_SCENES,
  MATERIAL_SOURCE_FILTERS,
  MATERIAL_TYPES,
  buildAutoTags,
  labelOf,
  mergeTags,
} from '../data/materialOptions.js'
import {
  aiTagAndSaveMaterial,
  createMaterialRecord,
  deleteMaterial,
  fetchMaterials,
  syncMaterialsFromDisk,
} from '../lib/materialsApi.js'

const props = defineProps({
  sceneOnly: { type: Boolean, default: false },
})

const emit = defineEmits(['toast', 'error'])

const categoryTabs = computed(() =>
  props.sceneOnly
    ? MATERIAL_CATEGORY_TABS.filter((t) => t.value !== 'character')
    : MATERIAL_CATEGORY_TABS,
)

const items = ref([])
const loading = ref(false)
const saving = ref(false)
const previewUrl = ref('')

const filters = ref({
  type: props.sceneOnly ? 'scene' : '',
  role: '',
  emotion: '',
  tag: '',
  aiGenerated: '',
})

const form = ref({
  name: '',
  type: 'character',
  role: 'programmer',
  emotion: 'normal',
  scene: 'office',
  tagsText: '',
  url: '',
  uploadId: '',
})

const selectedFile = ref(/** @type {File|null} */ (null))
const advancedOpen = ref(false)

const autoTags = computed(() =>
  buildAutoTags({
    type: form.value.type,
    role: form.value.role,
    emotion: form.value.emotion,
    scene: form.value.scene,
  }),
)

const finalTagsPreview = computed(() =>
  mergeTags(parseTags(form.value.tagsText), autoTags.value),
)

function resetForm() {
  form.value = {
    name: '',
    type: 'character',
    role: 'programmer',
    emotion: 'normal',
    scene: 'office',
    tagsText: '',
    url: '',
    uploadId: '',
  }
  selectedFile.value = null
  previewUrl.value = ''
  advancedOpen.value = false
}

function parseTags(text) {
  return String(text || '')
    .replace(/，/g, ',')
    .split(',')
    .map((t) => t.trim().toLowerCase())
    .filter(Boolean)
}

async function loadList() {
  loading.value = true
  await syncMaterialsFromDisk()
  const res = await fetchMaterials({
    type: filters.value.type,
    role: filters.value.role,
    emotion: filters.value.emotion,
    tag: filters.value.tag,
    aiGenerated: filters.value.aiGenerated,
  })
  loading.value = false
  if (!res.ok) {
    emit('error', res.message)
    return
  }
  items.value = res.data
}

function onFileChange(event) {
  const file = event.target.files?.[0]
  if (!file) return
  const name = (file.name || '').toLowerCase()
  if (name.endsWith('.svg') || file.type === 'image/svg+xml') {
    emit('error', '暂不支持 SVG，请上传 PNG/JPG')
    event.target.value = ''
    return
  }
  const ok =
    ['image/png', 'image/jpeg', 'image/webp'].includes(file.type) ||
    /\.(png|jpe?g|webp)$/i.test(name)
  if (!ok) {
    emit('error', '仅支持 png / jpg / jpeg / webp')
    event.target.value = ''
    return
  }
  selectedFile.value = file
  previewUrl.value = URL.createObjectURL(file)
}

async function aiTagAndSave() {
  if (!selectedFile.value) {
    emit('error', '请先选择图片')
    return
  }
  if (!form.value.role) {
    emit('error', '请选择职业角色')
    return
  }

  saving.value = true
  const res = await aiTagAndSaveMaterial(selectedFile.value, {
    role: form.value.role,
    name: (form.value.name || '').trim(),
  })
  saving.value = false

  if (!res.ok) {
    emit('error', res.message)
    return
  }

  const hint = res.data.tagSource === 'ai' ? 'AI 已识别并保存' : '已用默认标签保存（AI 暂不可用）'
  emit('toast', hint)
  resetForm()
  await loadList()
}

async function saveMaterialManual() {
  if (!form.value.url) {
    emit('error', '请先通过 AI 识别并保存，或在高级编辑中填写 URL')
    return
  }
  saving.value = true
  const res = await createMaterialRecord({
    id: form.value.uploadId || undefined,
    name: (form.value.name || '').trim() || '未命名素材',
    type: form.value.type,
    role: form.value.role,
    emotion: form.value.emotion,
    scene: form.value.scene,
    url: form.value.url,
    tags: mergeTags(parseTags(form.value.tagsText), autoTags.value),
  })
  saving.value = false
  if (!res.ok) {
    emit('error', res.message)
    return
  }
  emit('toast', '素材已保存')
  resetForm()
  await loadList()
}

async function removeItem(id) {
  if (!window.confirm('确定删除这条素材吗？')) return
  const res = await deleteMaterial(id)
  if (!res.ok) {
    emit('error', res.message)
    return
  }
  emit('toast', '已删除')
  await loadList()
}

onMounted(() => {
  loadList()
})
</script>

<template>
  <div class="materials">
    <section v-if="sceneOnly" class="card upload-section scene-hint">
      <h2 class="section-title">场景 / UI / 道具素材</h2>
      <p class="section-sub">
        人物角色请在「角色 IP」页管理。此处仅管理场景、界面、道具等非人物素材（高级模式）。
      </p>
    </section>

    <section v-else class="card upload-section">
      <h2 class="section-title">上传人物素材</h2>
      <p class="section-sub">
        人物角色已迁移至「角色 IP」页。此处保留兼容上传，建议使用角色 IP 工作台。
      </p>

      <label class="file-label">
        <input
          type="file"
          accept="image/png,image/jpeg,image/jpg,image/webp,.png,.jpg,.jpeg,.webp"
          class="file-input"
          @change="onFileChange"
        />
        <span class="file-btn">选择图片 <span class="req">*</span></span>
      </label>

      <div v-if="previewUrl" class="preview-wrap">
        <img class="preview-img" :src="previewUrl" alt="预览" />
      </div>

      <div class="simple-form">
        <label class="field">
          <span class="label">职业角色 <span class="req">*</span></span>
          <select v-model="form.role" class="input">
            <option v-for="o in MATERIAL_ROLES_UPLOAD" :key="o.value" :value="o.value">
              {{ o.label }}
            </option>
          </select>
        </label>
        <label class="field">
          <span class="label">素材名称（可选）</span>
          <input v-model="form.name" class="input" placeholder="不填则由 AI 自动命名" />
        </label>
      </div>

      <button type="button" class="btn-save btn-gradient" :disabled="saving" @click="aiTagAndSave">
        {{ saving ? 'AI 识别中…' : 'AI 识别并保存' }}
      </button>

      <button type="button" class="btn-advanced-toggle" @click="advancedOpen = !advancedOpen">
        {{ advancedOpen ? '收起高级编辑' : '展开高级编辑（手动调整类型/情绪/场景/标签）' }}
      </button>

      <div v-if="advancedOpen" class="advanced-panel">
        <p class="advanced-hint">一般无需手动编辑；保存后如需微调可在此修改并再次保存。</p>
        <div class="form-grid">
          <label class="field">
            <span class="label">素材类型</span>
            <select v-model="form.type" class="input">
              <option v-for="o in MATERIAL_TYPES" :key="o.value" :value="o.value">{{ o.label }}</option>
            </select>
          </label>
          <label class="field">
            <span class="label">情绪</span>
            <select v-model="form.emotion" class="input">
              <option v-for="o in MATERIAL_EMOTIONS" :key="o.value" :value="o.value">{{ o.label }}</option>
            </select>
          </label>
          <label class="field">
            <span class="label">场景</span>
            <select v-model="form.scene" class="input">
              <option v-for="o in MATERIAL_SCENES" :key="o.value" :value="o.value">{{ o.label }}</option>
            </select>
          </label>
          <label class="field field--full">
            <span class="label">标签（逗号分隔）</span>
            <input v-model="form.tagsText" class="input" placeholder="programmer,tired,night_office" />
          </label>
          <label v-if="form.url" class="field field--full">
            <span class="label">图片 URL</span>
            <input v-model="form.url" class="input" readonly />
          </label>
        </div>
        <button type="button" class="btn-secondary" :disabled="saving || !form.url" @click="saveMaterialManual">
          手动保存修改
        </button>
      </div>
    </section>

    <section class="card list-section">
      <div class="list-head">
        <h2 class="section-title">素材列表</h2>
        <button type="button" class="btn-refresh" :disabled="loading" @click="loadList">刷新</button>
      </div>

      <div class="category-tabs">
        <button
          v-for="tab in categoryTabs"
          :key="tab.value"
          type="button"
          class="tab-btn"
          :class="{ 'tab-btn--active': filters.type === tab.value }"
          @click="filters.type = tab.value; loadList()"
        >
          {{ tab.label }}
        </button>
      </div>

      <div class="filters">
        <select v-model="filters.aiGenerated" class="input input--sm" @change="loadList">
          <option v-for="o in MATERIAL_SOURCE_FILTERS" :key="o.value" :value="o.value">
            {{ o.label }}
          </option>
        </select>
        <select v-model="filters.type" class="input input--sm" @change="loadList">
          <option value="">全部类型</option>
          <option v-for="o in MATERIAL_TYPES" :key="o.value" :value="o.value">{{ o.label }}</option>
        </select>
        <select v-model="filters.role" class="input input--sm" @change="loadList">
          <option value="">全部职业</option>
          <option v-for="o in MATERIAL_ROLES.filter((x) => x.value !== 'none')" :key="o.value" :value="o.value">
            {{ o.label }}
          </option>
        </select>
        <select v-model="filters.emotion" class="input input--sm" @change="loadList">
          <option value="">全部情绪</option>
          <option v-for="o in MATERIAL_EMOTIONS.filter((x) => x.value !== 'none')" :key="o.value" :value="o.value">
            {{ o.label }}
          </option>
        </select>
        <input
          v-model="filters.tag"
          class="input input--sm"
          placeholder="标签关键词"
          @keyup.enter="loadList"
        />
        <button type="button" class="btn-filter" @click="loadList">筛选</button>
      </div>

      <p v-if="loading" class="hint">加载中…</p>
      <p v-else-if="!items.length" class="hint">暂无素材，请先上传。</p>

      <ul v-else class="material-list">
        <li v-for="item in items" :key="item.id" class="material-item">
          <img class="thumb" :src="item.url" :alt="item.name" loading="lazy" />
          <div class="item-body">
            <p class="item-name">
              {{ item.name }}
              <span v-if="item.aiGenerated" class="badge badge--ai">AI 生成</span>
              <span v-else class="badge badge--manual">手动上传</span>
            </p>
            <p class="item-meta">
              {{ labelOf(MATERIAL_TYPES, item.type) }} ·
              {{ labelOf(MATERIAL_ROLES, item.role) }} ·
              {{ labelOf(MATERIAL_EMOTIONS, item.emotion) }}
            </p>
            <p class="item-meta">场景：{{ labelOf(MATERIAL_SCENES, item.scene) }}</p>
            <p v-if="item.imageWidth" class="item-debug">
              尺寸 {{ item.imageWidth }}×{{ item.imageHeight }} · {{ item.aspectRatio }}
              · {{ item.isVertical ? '竖屏 ✓' : '横图 ✗' }}
            </p>
            <p class="item-tags">
              <span v-for="t in item.tags" :key="t" class="tag">{{ t }}</span>
            </p>
            <p class="item-url">{{ item.url }}</p>
            <p class="item-time">{{ item.createdAt }}</p>
            <button type="button" class="btn-delete" @click="removeItem(item.id)">删除</button>
          </div>
        </li>
      </ul>
    </section>
  </div>
</template>

<style scoped>
.materials {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card {
  background: var(--surface-solid);
  border-radius: var(--radius);
  padding: 18px 16px;
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
}

.section-title {
  margin: 0 0 6px;
  font-size: 17px;
  font-weight: 800;
  color: var(--text);
}

.section-sub {
  margin: 0 0 14px;
  font-size: 13px;
  color: var(--text-muted);
  line-height: 1.55;
}

.file-label {
  display: inline-block;
  margin-bottom: 12px;
}

.file-input {
  display: none;
}

.file-btn {
  display: inline-block;
  padding: 10px 16px;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  color: #5b21b6;
  background: rgba(99, 102, 241, 0.1);
  border: 1px dashed rgba(99, 102, 241, 0.35);
  cursor: pointer;
}

.preview-wrap {
  margin-bottom: 14px;
}

.preview-img {
  width: 100%;
  max-height: 200px;
  object-fit: contain;
  border-radius: 12px;
  background: #f1f5f9;
  margin-bottom: 10px;
}

.form-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 14px;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.field--full {
  grid-column: 1 / -1;
}

.label {
  font-size: 12px;
  font-weight: 700;
  color: var(--text-muted);
}

.tag-hint {
  margin: 6px 0 0;
  font-size: 12px;
  line-height: 1.6;
  color: var(--text-muted);
}

.tag-chip {
  display: inline-block;
  margin: 2px 4px 2px 0;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 11px;
  font-family: ui-monospace, monospace;
  background: rgba(16, 185, 129, 0.12);
  color: #047857;
}

.tag-muted {
  color: #94a3b8;
}

.tag-preview {
  margin: 6px 0 0;
  font-size: 11px;
  color: #6366f1;
  word-break: break-all;
}

.input {
  padding: 10px 12px;
  border-radius: 10px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  font-size: 14px;
}

.input--sm {
  font-size: 13px;
  padding: 8px 10px;
}

.btn-secondary {
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  border: 1px solid rgba(99, 102, 241, 0.28);
  background: #fff;
  color: #5b21b6;
  cursor: pointer;
}

.simple-form {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-bottom: 14px;
}

.req {
  color: #ef4444;
}

.btn-save {
  width: 100%;
  padding: 13px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  cursor: pointer;
}

.btn-advanced-toggle {
  display: block;
  width: 100%;
  margin-top: 10px;
  padding: 8px 0;
  border: none;
  background: transparent;
  font-size: 13px;
  color: #6366f1;
  cursor: pointer;
  text-align: center;
}

.advanced-panel {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px dashed rgba(148, 163, 184, 0.4);
}

.advanced-hint {
  margin: 0 0 12px;
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
}

.list-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.btn-refresh {
  padding: 6px 12px;
  font-size: 13px;
  font-weight: 600;
  color: #6366f1;
  background: transparent;
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: 8px;
  cursor: pointer;
}

.category-tabs {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.tab-btn {
  padding: 6px 12px;
  border-radius: 999px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: #fff;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  cursor: pointer;
}

.tab-btn--active {
  border-color: rgba(99, 102, 241, 0.45);
  background: rgba(99, 102, 241, 0.1);
  color: #5b21b6;
}

.filters {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 14px;
}

.badge {
  display: inline-block;
  margin-left: 6px;
  padding: 2px 8px;
  border-radius: 999px;
  font-size: 10px;
  font-weight: 700;
  vertical-align: middle;
}

.badge--ai {
  background: rgba(16, 185, 129, 0.15);
  color: #047857;
}

.badge--manual {
  background: rgba(99, 102, 241, 0.12);
  color: #5b21b6;
}

.btn-filter {
  padding: 8px 14px;
  border-radius: 10px;
  font-size: 13px;
  font-weight: 600;
  border: none;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  color: #fff;
  cursor: pointer;
}

.hint {
  margin: 0;
  font-size: 14px;
  color: var(--text-muted);
  text-align: center;
  padding: 24px 0;
}

.material-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.material-item {
  display: flex;
  gap: 12px;
  padding: 12px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.25);
  background: rgba(255, 255, 255, 0.6);
}

.thumb {
  width: 96px;
  height: 96px;
  object-fit: cover;
  border-radius: 10px;
  flex-shrink: 0;
  background: #eef2ff;
}

.item-body {
  flex: 1;
  min-width: 0;
}

.item-name {
  margin: 0 0 4px;
  font-size: 15px;
  font-weight: 700;
}

.item-meta {
  margin: 0 0 4px;
  font-size: 12px;
  color: var(--text-muted);
}

.item-debug {
  margin: 0 0 6px;
  font-size: 11px;
  font-weight: 600;
  color: #5b21b6;
  font-family: ui-monospace, monospace;
}

.item-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  margin: 6px 0;
}

.tag {
  font-size: 10px;
  padding: 2px 6px;
  border-radius: 4px;
  background: rgba(99, 102, 241, 0.1);
  color: #5b21b6;
  font-family: ui-monospace, monospace;
}

.item-url {
  margin: 0;
  font-size: 11px;
  color: #94a3b8;
  word-break: break-all;
}

.item-time {
  margin: 4px 0 8px;
  font-size: 11px;
  color: #94a3b8;
}

.btn-delete {
  padding: 6px 12px;
  font-size: 12px;
  font-weight: 600;
  color: #b91c1c;
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 8px;
  cursor: pointer;
}

@media (max-width: 480px) {
  .form-grid,
  .simple-form {
    grid-template-columns: 1fr;
  }
}
</style>
