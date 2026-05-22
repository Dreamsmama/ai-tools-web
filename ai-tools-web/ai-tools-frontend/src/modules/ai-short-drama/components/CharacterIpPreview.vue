<script setup>
import { computed, onMounted, ref, watch } from 'vue'
import { RouterLink } from 'vue-router'
import { CAREER_OPTION_AUTO } from '../data/options.js'
import { careerToRoleKey as legacyCareerToRoleKey, roleLabel } from '../data/characterRoles.js'
import { fetchCharacterIpWorkbench } from '../lib/characterIpApi.js'
import { useProfessionStore } from '../stores/professionStore.js'

const { ensureLoaded, careerToRoleKey: storeCareerToRoleKey } = useProfessionStore()

const props = defineProps({
  career: { type: String, default: '' },
})

const loading = ref(false)
/** @type {import('vue').Ref<Array<{ role: string, roleLabel: string, configured: boolean, active?: { baseImageUrl?: string, name?: string } }>>} */
const roles = ref([])

const selectedRoleKey = computed(() => {
  const cn = (props.career || '').trim()
  if (!cn || cn === CAREER_OPTION_AUTO) return ''
  return storeCareerToRoleKey(cn) || legacyCareerToRoleKey(cn)
})

const selectedSlot = computed(() => {
  if (!selectedRoleKey.value) return null
  return roles.value.find((r) => r.role === selectedRoleKey.value) || null
})

const configuredCount = computed(() => roles.value.filter((r) => r.configured).length)

async function loadRoles() {
  loading.value = true
  try {
    const res = await fetchCharacterIpWorkbench()
    if (res.ok) {
      roles.value = res.data?.roles || []
    }
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await ensureLoaded()
  await loadRoles()
})
watch(() => props.career, () => {}, { flush: 'post' })
</script>

<template>
  <section class="char-preview card" aria-label="角色 IP 状态">
    <div class="char-preview-head">
      <div>
        <p class="char-preview-kicker">成片人物</p>
        <p class="char-preview-title">基础角色 IP</p>
      </div>
      <RouterLink class="char-preview-link" to="/tools/ai-short-drama/characters">管理角色 →</RouterLink>
    </div>

    <p v-if="loading && !roles.length" class="char-preview-hint">加载角色库…</p>

    <template v-else-if="selectedSlot">
      <div v-if="selectedSlot.configured && selectedSlot.active" class="char-preview-active">
        <img
          :src="selectedSlot.active.baseImageUrl"
          :alt="selectedSlot.roleLabel"
          class="char-preview-thumb"
          loading="lazy"
        />
        <div class="char-preview-meta">
          <p class="char-preview-role">{{ selectedSlot.roleLabel || roleLabel(selectedSlot.role) }}</p>
          <p class="char-preview-status char-preview-status--ok">已配置 · 成片将使用该角色</p>
          <p class="char-preview-name">{{ selectedSlot.active.name || '当前基础角色' }}</p>
        </div>
      </div>
      <div v-else class="char-preview-warn">
        <p class="char-preview-role">{{ selectedSlot.roleLabel || roleLabel(selectedSlot.role) }}</p>
        <p class="char-preview-status char-preview-status--warn">
          尚未确认基础角色，人物镜头可能无法生成
        </p>
        <RouterLink class="char-preview-cta" to="/tools/ai-short-drama/characters">
          去配置 {{ selectedSlot.roleLabel }} 角色
        </RouterLink>
      </div>
    </template>

    <template v-else>
      <p class="char-preview-hint">
        将按文案自动识别职业。已配置 {{ configuredCount }}/{{ roles.length || 6 }} 个职业角色。
      </p>
      <ul v-if="roles.length" class="char-preview-grid">
        <li
          v-for="slot in roles"
          :key="slot.role"
          class="char-dot"
          :class="slot.configured ? 'char-dot--ok' : 'char-dot--empty'"
          :title="`${slot.roleLabel}${slot.configured ? ' · 已配置' : ' · 未配置'}`"
        >
          <img
            v-if="slot.active?.baseImageUrl"
            :src="slot.active.baseImageUrl"
            :alt="slot.roleLabel"
            class="char-dot-img"
          />
          <span v-else class="char-dot-placeholder">{{ (slot.roleLabel || slot.role)[0] }}</span>
        </li>
      </ul>
    </template>
  </section>
</template>

<style scoped>
.card {
  background: var(--surface-solid);
  border-radius: var(--radius);
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
}

.char-preview {
  padding: 14px 16px;
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.06), rgba(168, 85, 247, 0.04));
}

.char-preview-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 12px;
  margin-bottom: 10px;
}

.char-preview-kicker {
  margin: 0 0 2px;
  font-size: 11px;
  font-weight: 700;
  color: #6366f1;
}

.char-preview-title {
  margin: 0;
  font-size: 14px;
  font-weight: 800;
  color: var(--text);
}

.char-preview-link {
  flex-shrink: 0;
  font-size: 12px;
  font-weight: 700;
  color: #4f46e5;
  text-decoration: none;
}

.char-preview-hint {
  margin: 0;
  font-size: 12px;
  line-height: 1.55;
  color: var(--text-muted);
}

.char-preview-active {
  display: flex;
  gap: 12px;
  align-items: center;
}

.char-preview-thumb {
  width: 56px;
  height: 84px;
  object-fit: cover;
  object-position: top center;
  border-radius: 10px;
  border: 2px solid rgba(99, 102, 241, 0.35);
  flex-shrink: 0;
}

.char-preview-meta {
  min-width: 0;
}

.char-preview-role {
  margin: 0 0 4px;
  font-size: 15px;
  font-weight: 800;
}

.char-preview-name {
  margin: 4px 0 0;
  font-size: 12px;
  color: var(--text-muted);
}

.char-preview-status {
  margin: 0;
  font-size: 12px;
  font-weight: 600;
}

.char-preview-status--ok {
  color: #047857;
}

.char-preview-status--warn {
  color: #b45309;
}

.char-preview-warn {
  padding: 10px 12px;
  border-radius: 12px;
  background: rgba(245, 158, 11, 0.08);
  border: 1px solid rgba(245, 158, 11, 0.25);
}

.char-preview-cta {
  display: inline-block;
  margin-top: 8px;
  font-size: 12px;
  font-weight: 700;
  color: #4f46e5;
  text-decoration: none;
}

.char-preview-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  list-style: none;
  margin: 10px 0 0;
  padding: 0;
}

.char-dot {
  width: 40px;
  height: 56px;
  border-radius: 8px;
  overflow: hidden;
  border: 2px solid rgba(148, 163, 184, 0.35);
}

.char-dot--ok {
  border-color: rgba(16, 185, 129, 0.55);
}

.char-dot-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.char-dot-placeholder {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 100%;
  height: 100%;
  font-size: 14px;
  font-weight: 800;
  color: #94a3b8;
  background: #f1f5f9;
}
</style>
