import { ref } from 'vue'
import { CHARACTER_ROLES } from '../data/characterRoles.js'
import { fetchProfessions } from '../lib/characterIpApi.js'

/** @type {import('vue').Ref<Array<{ id: string, roleKey: string, name: string, description?: string, styleHint?: string }>>} */
const professions = ref([])
const loaded = ref(false)
const loading = ref(false)

export function useProfessionStore() {
  async function ensureLoaded(force = false) {
    if (loaded.value && !force) return { ok: true }
    loading.value = true
    try {
      const res = await fetchProfessions()
      if (res.ok && res.data?.length) {
        professions.value = res.data
        loaded.value = true
      } else if (!professions.value.length) {
        professions.value = CHARACTER_ROLES.map((r) => ({
          id: `prof_${r.value}`,
          roleKey: r.value,
          name: r.label,
          description: '',
          styleHint: '',
          builtIn: true,
        }))
        loaded.value = true
      }
      return res
    } finally {
      loading.value = false
    }
  }

  function careerOptions() {
    return professions.value.map((p) => p.name).filter(Boolean)
  }

  function careerToRoleKey(careerCn) {
    const cn = (careerCn || '').trim()
    const hit = professions.value.find((p) => p.name === cn)
    return hit?.roleKey || ''
  }

  function roleKeyToName(roleKey) {
    const hit = professions.value.find((p) => p.roleKey === roleKey)
    return hit?.name || roleKey
  }

  return {
    professions,
    loaded,
    loading,
    ensureLoaded,
    careerOptions,
    careerToRoleKey,
    roleKeyToName,
  }
}
