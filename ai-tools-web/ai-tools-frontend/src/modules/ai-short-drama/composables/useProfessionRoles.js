import { computed, ref } from 'vue'
import {
  activateCharacterIp,
  aiGenerateCharacterIpCandidates,
  createProfession,
  deleteCharacterIp,
  deleteProfession,
  fetchCharacterIpWorkbench,
  fetchProfessions,
  updateProfession,
  uploadCharacterIpBase,
} from '../lib/characterIpApi.js'

/**
 * @typedef {Object} ProfessionRole
 * @property {string} id
 * @property {string} professionId
 * @property {string} role
 * @property {string} profession
 * @property {string} [description]
 * @property {string} [styleHint]
 * @property {string} [avatar]
 * @property {boolean} isCurrent
 * @property {'pending'|'generated'|'empty'} status
 * @property {boolean} configured
 * @property {boolean} builtIn
 * @property {Array} pending
 */

export function useProfessionRoles() {
  const loading = ref(false)
  const actionRole = ref('')
  const actionId = ref('')
  const generatingRole = ref('')
  const loadError = ref('')
  /** @type {import('vue').Ref<ProfessionRole[]>} */
  const roles = ref([])

  function mapSlot(slot) {
    const active = slot.active
    const pending = slot.pending || []
    const hasPending = pending.length > 0
    const configured = Boolean(slot.configured && active)
    let status = 'empty'
    if (configured) status = 'generated'
    else if (hasPending) status = 'pending'

    return {
      id: slot.professionId || slot.role,
      professionId: slot.professionId || '',
      role: slot.role,
      profession: slot.roleLabel || slot.role,
      description: slot.description || '',
      styleHint: slot.styleHint || '',
      avatar: active?.baseImageUrl || '',
      isCurrent: configured,
      status,
      configured,
      builtIn: Boolean(slot.builtIn),
      active,
      pending,
    }
  }

  function mapProfessionOnly(p) {
    return {
      id: p.id || p.roleKey,
      professionId: p.id || '',
      role: p.roleKey,
      profession: p.name || p.roleKey,
      description: p.description || '',
      styleHint: p.styleHint || '',
      avatar: '',
      isCurrent: false,
      status: 'empty',
      configured: false,
      builtIn: Boolean(p.builtIn),
      active: null,
      pending: [],
    }
  }

  async function loadRoles() {
    loading.value = true
    loadError.value = ''
    try {
      // 先拉职业列表（轻量）；与 workbench 均有 8s 超时，避免后端被 /generate 堵住时无限「加载角色库…」
      const profRes = await fetchProfessions()
      if (profRes.ok && profRes.data?.length) {
        roles.value = profRes.data.map(mapProfessionOnly)
      } else if (!profRes.ok) {
        loadError.value = profRes.message || '职业列表加载失败'
      }

      const res = await fetchCharacterIpWorkbench()
      if (res.ok && res.data?.roles?.length) {
        roles.value = res.data.roles.map(mapSlot)
        loadError.value = ''
        return { ok: true }
      }
      if (profRes.ok && profRes.data?.length) {
        if (!res.ok) {
          loadError.value =
            res.message || '角色图加载较慢，已显示职业列表；可稍后刷新'
        }
        return { ok: true, partial: true }
      }
      const msg = res.message || profRes.message || '无法连接后端，请确认服务已启动（端口 8000）'
      loadError.value = msg
      roles.value = []
      return { ok: false, message: msg }
    } finally {
      loading.value = false
    }
  }

  const isEmpty = computed(() => !loading.value && roles.value.length === 0)

  async function addProfession({ name, description, styleHint }) {
    const res = await createProfession({ name, description, styleHint })
    if (!res.ok) return res
    await loadRoles()
    return res
  }

  async function editProfession(professionId, { name, description, styleHint }) {
    const res = await updateProfession(professionId, { name, description, styleHint })
    if (!res.ok) return res
    await loadRoles()
    return res
  }

  async function removeProfession(professionId) {
    const res = await deleteProfession(professionId)
    if (!res.ok) return res
    await loadRoles()
    return res
  }

  async function generateRole(slot, extraPrompt = '') {
    generatingRole.value = slot.role
    const desc = [extraPrompt, slot.styleHint, slot.description].filter(Boolean).join('，')
    const res = await aiGenerateCharacterIpCandidates(slot.role, desc)
    generatingRole.value = ''
    if (!res.ok) return res
    await loadRoles()
    return res
  }

  async function setCurrentRole(ipId) {
    actionId.value = ipId
    try {
      const res = await activateCharacterIp(ipId)
      if (!res.ok) return res
      await loadRoles()
      return res
    } finally {
      actionId.value = ''
    }
  }

  async function removeCharacterIp(ipId) {
    actionId.value = ipId
    try {
      const res = await deleteCharacterIp(ipId)
      if (!res.ok) return res
      await loadRoles()
      return res
    } finally {
      actionId.value = ''
    }
  }

  async function uploadBaseImage(file, role) {
    actionRole.value = role
    try {
      const res = await uploadCharacterIpBase(file, role)
      if (!res.ok) return res
      await loadRoles()
      return res
    } finally {
      actionRole.value = ''
    }
  }

  /** 供生成页：中文职业名列表 */
  function careerNameOptions() {
    return roles.value.map((r) => r.profession).filter(Boolean)
  }

  function careerToRoleKey(careerCn) {
    const cn = (careerCn || '').trim()
    if (!cn) return ''
    const hit = roles.value.find((r) => r.profession === cn)
    return hit?.role || ''
  }

  return {
    loading,
    actionRole,
    actionId,
    generatingRole,
    loadError,
    roles,
    isEmpty,
    loadRoles,
    addProfession,
    editProfession,
    removeProfession,
    generateRole,
    setCurrentRole,
    removeCharacterIp,
    uploadBaseImage,
    careerNameOptions,
    careerToRoleKey,
  }
}
