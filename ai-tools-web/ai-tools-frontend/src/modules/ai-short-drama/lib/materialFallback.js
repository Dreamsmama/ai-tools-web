/** 无可用素材时的前端提示（不再回退纯色占位图） */

export const MISSING_MATERIAL_MSG = '缺少可用素材，请上传人物图或生成真实场景图'

/**
 * @param {{ url?: string, materialStatus?: string, materialError?: string } | null | undefined} material
 */
export function hasUsableMaterial(material) {
  if (!material) return false
  if (material.materialStatus === 'missing') return false
  if (material.source === 'missing') return false
  return Boolean((material.url || '').trim())
}

/**
 * @param {{ url?: string, materialStatus?: string, materialError?: string, name?: string } | null | undefined} material
 */
export function materialDisplayMessage(material) {
  if (!material) return MISSING_MATERIAL_MSG
  if (material.materialError) return material.materialError
  if (material.materialStatus === 'missing' || material.source === 'missing') {
    return material.name || MISSING_MATERIAL_MSG
  }
  return ''
}
