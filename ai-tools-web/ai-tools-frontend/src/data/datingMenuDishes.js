/** @typedef {'none'|'mild'|'hot'} SpicyLevel */
/** @typedef {'主菜'|'肉菜'|'素菜'|'主食'|'饮品'|'甜品'} DishCategory */

/**
 * @typedef {Object} Dish
 * @property {number} id
 * @property {string} name
 * @property {string} emoji
 * @property {string} cuisine
 * @property {DishCategory} category
 * @property {number} price
 * @property {SpicyLevel} spicy
 * @property {string[]} tags
 */

/** @type {Dish[]} */
export const DISHES = [
  { id: 1, name: '水煮鱼', emoji: '🐟', cuisine: '川菜', category: '主菜', price: 68, spicy: 'hot', tags: ['下饭', '含海鲜', '约会'] },
  { id: 2, name: '麻婆豆腐', emoji: '🌶️', cuisine: '川菜', category: '主菜', price: 28, spicy: 'hot', tags: ['下饭', '不踩雷'] },
  { id: 3, name: '宫保鸡丁', emoji: '🍗', cuisine: '川菜', category: '肉菜', price: 38, spicy: 'mild', tags: ['下饭', '约会'] },
  { id: 4, name: '回锅肉', emoji: '🥓', cuisine: '川菜', category: '肉菜', price: 42, spicy: 'mild', tags: ['下饭', '偏油'] },
  { id: 5, name: '鱼香肉丝', emoji: '🥢', cuisine: '川菜', category: '肉菜', price: 36, spicy: 'mild', tags: ['下饭', '不踩雷'] },
  { id: 6, name: '口水鸡', emoji: '🐔', cuisine: '川菜', category: '肉菜', price: 32, spicy: 'mild', tags: ['开胃', '约会'] },
  { id: 7, name: '蒜泥白肉', emoji: '🥩', cuisine: '川菜', category: '肉菜', price: 34, spicy: 'none', tags: ['开胃', '偏油'] },
  { id: 8, name: '干煸四季豆', emoji: '🫛', cuisine: '川菜', category: '素菜', price: 22, spicy: 'mild', tags: ['下饭', '偏油'] },
  { id: 9, name: '清炒时蔬', emoji: '🥬', cuisine: '川菜', category: '素菜', price: 18, spicy: 'none', tags: ['清淡', '健康'] },
  { id: 10, name: '担担面', emoji: '🍜', cuisine: '川菜', category: '主食', price: 22, spicy: 'hot', tags: ['快手', '下饭'] },

  { id: 11, name: '剁椒鱼头', emoji: '🐟', cuisine: '湘菜', category: '主菜', price: 78, spicy: 'hot', tags: ['下饭', '含海鲜', '约会'] },
  { id: 12, name: '小炒黄牛肉', emoji: '🥩', cuisine: '湘菜', category: '肉菜', price: 48, spicy: 'hot', tags: ['下饭', '不踩雷'] },
  { id: 13, name: '辣椒炒肉', emoji: '🌶️', cuisine: '湘菜', category: '肉菜', price: 36, spicy: 'hot', tags: ['下饭', '偏油'] },
  { id: 14, name: '毛氏红烧肉', emoji: '🍖', cuisine: '湘菜', category: '肉菜', price: 52, spicy: 'none', tags: ['约会', '偏油'] },
  { id: 15, name: '手撕包菜', emoji: '🥬', cuisine: '湘菜', category: '素菜', price: 18, spicy: 'mild', tags: ['下饭', '快手'] },
  { id: 16, name: '擂辣椒皮蛋', emoji: '🥚', cuisine: '湘菜', category: '素菜', price: 20, spicy: 'hot', tags: ['开胃', '不踩雷'] },
  { id: 17, name: '长沙米粉', emoji: '🍜', cuisine: '湘菜', category: '主食', price: 16, spicy: 'mild', tags: ['快手', '下班随便吃'] },

  { id: 18, name: '白切鸡', emoji: '🐔', cuisine: '粤菜', category: '主菜', price: 58, spicy: 'none', tags: ['清淡', '约会'] },
  { id: 19, name: '豉汁蒸排骨', emoji: '🍖', cuisine: '粤菜', category: '肉菜', price: 38, spicy: 'none', tags: ['下饭', '不踩雷'] },
  { id: 20, name: '蜜汁叉烧', emoji: '🥓', cuisine: '粤菜', category: '肉菜', price: 42, spicy: 'none', tags: ['约会', '偏油'] },
  { id: 21, name: '干炒牛河', emoji: '🍜', cuisine: '粤菜', category: '主食', price: 28, spicy: 'none', tags: ['快手', '下饭'] },
  { id: 22, name: '虾饺皇', emoji: '🦐', cuisine: '粤菜', category: '主菜', price: 32, spicy: 'none', tags: ['约会', '含海鲜'] },
  { id: 23, name: '上汤娃娃菜', emoji: '🥬', cuisine: '粤菜', category: '素菜', price: 22, spicy: 'none', tags: ['清淡', '健康'] },
  { id: 24, name: '广式煲仔饭', emoji: '🍚', cuisine: '粤菜', category: '主食', price: 32, spicy: 'none', tags: ['下饭', '周末改善伙食'] },

  { id: 25, name: '锅包肉', emoji: '🥩', cuisine: '东北菜', category: '肉菜', price: 48, spicy: 'none', tags: ['约会', '偏油'] },
  { id: 26, name: '地三鲜', emoji: '🍆', cuisine: '东北菜', category: '素菜', price: 24, spicy: 'none', tags: ['下饭', '偏油'] },
  { id: 27, name: '小鸡炖蘑菇', emoji: '🍲', cuisine: '东北菜', category: '主菜', price: 58, spicy: 'none', tags: ['下饭', '周末改善伙食'] },
  { id: 28, name: '东北乱炖', emoji: '🥘', cuisine: '东北菜', category: '主菜', price: 52, spicy: 'none', tags: ['下饭', '不踩雷'] },
  { id: 29, name: '猪肉炖粉条', emoji: '🍜', cuisine: '东北菜', category: '主菜', price: 46, spicy: 'none', tags: ['下饭', '偏油'] },
  { id: 30, name: '大拉皮', emoji: '🥗', cuisine: '东北菜', category: '素菜', price: 18, spicy: 'mild', tags: ['开胃', '含香菜'] },

  { id: 31, name: '红烧肉', emoji: '🍖', cuisine: '上海菜', category: '肉菜', price: 48, spicy: 'none', tags: ['下饭', '约会', '偏油'] },
  { id: 32, name: '生煎包', emoji: '🥟', cuisine: '上海菜', category: '主食', price: 22, spicy: 'none', tags: ['快手', '不踩雷'] },
  { id: 33, name: '腌笃鲜', emoji: '🍲', cuisine: '上海菜', category: '主菜', price: 56, spicy: 'none', tags: ['清淡', '周末改善伙食'] },
  { id: 34, name: '油爆虾', emoji: '🦐', cuisine: '上海菜', category: '主菜', price: 62, spicy: 'none', tags: ['约会', '含海鲜', '偏油'] },
  { id: 35, name: '清炒河虾仁', emoji: '🦐', cuisine: '上海菜', category: '肉菜', price: 58, spicy: 'none', tags: ['清淡', '含海鲜'] },

  { id: 36, name: '北京烤鸭', emoji: '🦆', cuisine: '北京菜', category: '主菜', price: 128, spicy: 'none', tags: ['约会', '周末改善伙食'] },
  { id: 37, name: '京酱肉丝', emoji: '🥩', cuisine: '北京菜', category: '肉菜', price: 42, spicy: 'none', tags: ['下饭', '不踩雷'] },
  { id: 38, name: '炸酱面', emoji: '🍜', cuisine: '北京菜', category: '主食', price: 24, spicy: 'none', tags: ['快手', '下班随便吃'] },
  { id: 39, name: '爆肚', emoji: '🥘', cuisine: '北京菜', category: '肉菜', price: 48, spicy: 'mild', tags: ['开胃', '偏油'] },
  { id: 40, name: '豌豆黄', emoji: '🍮', cuisine: '北京菜', category: '甜品', price: 16, spicy: 'none', tags: ['哄女朋友开心', '清淡'] },

  { id: 41, name: '羊肉泡馍', emoji: '🍲', cuisine: '西北菜', category: '主菜', price: 38, spicy: 'mild', tags: ['下饭', '周末改善伙食'] },
  { id: 42, name: '肉夹馍', emoji: '🥙', cuisine: '西北菜', category: '主食', price: 18, spicy: 'mild', tags: ['快手', '下班随便吃'] },
  { id: 43, name: '凉皮', emoji: '🥗', cuisine: '西北菜', category: '主食', price: 14, spicy: 'mild', tags: ['快手', '含香菜'] },
  { id: 44, name: '大盘鸡', emoji: '🍗', cuisine: '西北菜', category: '主菜', price: 68, spicy: 'mild', tags: ['下饭', '不踩雷'] },

  { id: 45, name: '新疆烤羊肉串', emoji: '🍢', cuisine: '新疆菜', category: '肉菜', price: 36, spicy: 'mild', tags: ['约会', '偏油'] },
  { id: 46, name: '手抓饭', emoji: '🍚', cuisine: '新疆菜', category: '主食', price: 32, spicy: 'none', tags: ['下饭', '偏油'] },
  { id: 47, name: '新疆大盘肚', emoji: '🥘', cuisine: '新疆菜', category: '主菜', price: 58, spicy: 'hot', tags: ['下饭', '偏油'] },

  { id: 48, name: '过桥米线', emoji: '🍜', cuisine: '云南菜', category: '主菜', price: 38, spicy: 'mild', tags: ['约会', '不踩雷'] },
  { id: 49, name: '汽锅鸡', emoji: '🍲', cuisine: '云南菜', category: '主菜', price: 68, spicy: 'none', tags: ['清淡', '周末改善伙食'] },
  { id: 50, name: '烤乳扇', emoji: '🧀', cuisine: '云南菜', category: '甜品', price: 22, spicy: 'none', tags: ['哄女朋友开心', '约会'] },

  { id: 51, name: '酸汤鱼', emoji: '🐟', cuisine: '贵州菜', category: '主菜', price: 62, spicy: 'mild', tags: ['开胃', '含海鲜'] },
  { id: 52, name: '丝娃娃', emoji: '🥬', cuisine: '贵州菜', category: '素菜', price: 28, spicy: 'mild', tags: ['健康', '含香菜'] },

  { id: 53, name: '热干面', emoji: '🍜', cuisine: '湖北菜', category: '主食', price: 16, spicy: 'mild', tags: ['快手', '下班随便吃'] },
  { id: 54, name: '武昌鱼', emoji: '🐟', cuisine: '湖北菜', category: '主菜', price: 72, spicy: 'mild', tags: ['约会', '含海鲜'] },
  { id: 55, name: '藕汤', emoji: '🍲', cuisine: '湖北菜', category: '主菜', price: 38, spicy: 'none', tags: ['清淡', '健康'] },

  { id: 56, name: '三文鱼刺身', emoji: '🍣', cuisine: '日料', category: '主菜', price: 68, spicy: 'none', tags: ['约会', '含海鲜', '周末改善伙食'] },
  { id: 57, name: '鳗鱼饭', emoji: '🍱', cuisine: '日料', category: '主食', price: 48, spicy: 'none', tags: ['约会', '含海鲜'] },
  { id: 58, name: '天妇罗', emoji: '🍤', cuisine: '日料', category: '肉菜', price: 42, spicy: 'none', tags: ['偏油', '含海鲜'] },
  { id: 59, name: '豚骨拉面', emoji: '🍜', cuisine: '日料', category: '主食', price: 38, spicy: 'none', tags: ['快手', '下班随便吃'] },
  { id: 60, name: '日式茶碗蒸', emoji: '🥚', cuisine: '日料', category: '素菜', price: 18, spicy: 'none', tags: ['清淡', '健康'] },
  { id: 61, name: '抹茶布丁', emoji: '🍮', cuisine: '日料', category: '甜品', price: 22, spicy: 'none', tags: ['哄女朋友开心', '约会'] },

  { id: 62, name: '部队锅', emoji: '🍲', cuisine: '韩餐', category: '主菜', price: 58, spicy: 'mild', tags: ['约会', '下饭'] },
  { id: 63, name: '韩式炸鸡', emoji: '🍗', cuisine: '韩餐', category: '肉菜', price: 48, spicy: 'mild', tags: ['偏油', '不踩雷'] },
  { id: 64, name: '石锅拌饭', emoji: '🍚', cuisine: '韩餐', category: '主食', price: 32, spicy: 'mild', tags: ['下饭', '快手'] },
  { id: 65, name: '泡菜汤', emoji: '🥘', cuisine: '韩餐', category: '主菜', price: 36, spicy: 'hot', tags: ['开胃', '下饭'] },

  { id: 66, name: '冬阴功汤', emoji: '🍲', cuisine: '泰餐', category: '主菜', price: 48, spicy: 'hot', tags: ['开胃', '含海鲜'] },
  { id: 67, name: '泰式炒河粉', emoji: '🍜', cuisine: '泰餐', category: '主食', price: 32, spicy: 'mild', tags: ['约会', '含海鲜'] },
  { id: 68, name: '芒果糯米饭', emoji: '🥭', cuisine: '泰餐', category: '甜品', price: 28, spicy: 'none', tags: ['哄女朋友开心', '约会'] },

  { id: 69, name: '越南河粉', emoji: '🍜', cuisine: '越南菜', category: '主菜', price: 32, spicy: 'none', tags: ['清淡', '健康'] },
  { id: 70, name: '春卷', emoji: '🥗', cuisine: '越南菜', category: '素菜', price: 24, spicy: 'none', tags: ['健康', '含香菜'] },

  { id: 71, name: '牛排', emoji: '🥩', cuisine: '西餐', category: '主菜', price: 128, spicy: 'none', tags: ['约会', '周末改善伙食'] },
  { id: 72, name: '意面', emoji: '🍝', cuisine: '西餐', category: '主食', price: 42, spicy: 'none', tags: ['约会', '不踩雷'] },
  { id: 73, name: '奶油蘑菇汤', emoji: '🍲', cuisine: '西餐', category: '主菜', price: 32, spicy: 'none', tags: ['清淡', '偏油'] },
  { id: 74, name: '凯撒沙拉', emoji: '🥗', cuisine: '西餐', category: '素菜', price: 28, spicy: 'none', tags: ['健康', '清淡'] },
  { id: 75, name: '提拉米苏', emoji: '🍰', cuisine: '西餐', category: '甜品', price: 32, spicy: 'none', tags: ['哄女朋友开心', '约会'] },

  { id: 76, name: '毛肚火锅', emoji: '🍲', cuisine: '火锅', category: '主菜', price: 88, spicy: 'hot', tags: ['约会', '周末改善伙食'] },
  { id: 77, name: '番茄锅底', emoji: '🍅', cuisine: '火锅', category: '主菜', price: 68, spicy: 'none', tags: ['清淡', '约会'] },
  { id: 78, name: '肥牛卷', emoji: '🥩', cuisine: '火锅', category: '肉菜', price: 38, spicy: 'none', tags: ['下饭', '不踩雷'] },
  { id: 79, name: '虾滑', emoji: '🦐', cuisine: '火锅', category: '肉菜', price: 36, spicy: 'none', tags: ['含海鲜', '约会'] },

  { id: 80, name: '烤羊排', emoji: '🍖', cuisine: '烧烤', category: '肉菜', price: 68, spicy: 'mild', tags: ['约会', '偏油'] },
  { id: 81, name: '烤茄子', emoji: '🍆', cuisine: '烧烤', category: '素菜', price: 18, spicy: 'mild', tags: ['下饭', '含香菜'] },
  { id: 82, name: '烤生蚝', emoji: '🦪', cuisine: '烧烤', category: '主菜', price: 48, spicy: 'mild', tags: ['含海鲜', '约会'] },

  { id: 83, name: '韩式烤肉', emoji: '🥩', cuisine: '烤肉', category: '主菜', price: 98, spicy: 'none', tags: ['约会', '周末改善伙食'] },
  { id: 84, name: '烤五花肉', emoji: '🥓', cuisine: '烤肉', category: '肉菜', price: 52, spicy: 'none', tags: ['偏油', '下饭'] },

  { id: 85, name: '小笼包', emoji: '🥟', cuisine: '小吃', category: '主食', price: 22, spicy: 'none', tags: ['快手', '不踩雷'] },
  { id: 86, name: '煎饼果子', emoji: '🥞', cuisine: '小吃', category: '主食', price: 12, spicy: 'none', tags: ['快手', '下班随便吃'] },
  { id: 87, name: '章鱼小丸子', emoji: '🐙', cuisine: '小吃', category: '主菜', price: 18, spicy: 'none', tags: ['含海鲜', '哄女朋友开心'] },

  { id: 88, name: '杨枝甘露', emoji: '🥤', cuisine: '甜品饮品', category: '饮品', price: 22, spicy: 'none', tags: ['哄女朋友开心', '约会'] },
  { id: 89, name: '珍珠奶茶', emoji: '🧋', cuisine: '甜品饮品', category: '饮品', price: 18, spicy: 'none', tags: ['不踩雷', '哄女朋友开心'] },
  { id: 90, name: '草莓蛋糕', emoji: '🍰', cuisine: '甜品饮品', category: '甜品', price: 38, spicy: 'none', tags: ['哄女朋友开心', '约会'] },
  { id: 91, name: '柠檬茶', emoji: '🍋', cuisine: '甜品饮品', category: '饮品', price: 16, spicy: 'none', tags: ['清爽', '不踩雷'] },
  { id: 92, name: '双皮奶', emoji: '🍮', cuisine: '甜品饮品', category: '甜品', price: 18, spicy: 'none', tags: ['哄女朋友开心', '清淡'] },
]

export const CUISINE_FILTERS = ['全部', '川菜', '湘菜', '粤菜', '东北菜', '日料', '韩餐', '火锅', '烧烤', '西餐', '甜品饮品']

export const CATEGORY_FILTERS = ['全部', '主菜', '肉菜', '素菜', '主食', '饮品', '甜品']

export const TASTE_OPTIONS = ['清淡', '微辣', '重辣']

export const SCENE_OPTIONS = ['约会', '下班随便吃', '周末改善伙食', '哄女朋友开心']

export const BUDGET_OPTIONS = ['50以内', '50-100', '100-200', '200+']

export const AVOID_OPTIONS = ['香菜', '海鲜', '太油', '太辣']

export const CATEGORY_META = {
  主菜: { emoji: '🍲', label: '主菜' },
  肉菜: { emoji: '🥩', label: '肉菜' },
  素菜: { emoji: '🥬', label: '素菜' },
  主食: { emoji: '🍚', label: '主食' },
  饮品: { emoji: '🥤', label: '饮品' },
  甜品: { emoji: '🍰', label: '甜品' },
}

export const TAGLINES = [
  '今天不纠结，直接吃这份',
  '这份菜单适合哄女朋友开心',
  '下班后就吃这个，稳',
  '适合两个人一起吃的幸福菜单',
]

export const KEYWORD_POOL = [
  '开胃｜下饭｜不踩雷',
  '浪漫｜约会｜仪式感',
  '快手｜省心｜不纠结',
  '周末｜改善伙食｜值得',
  '甜蜜｜治愈｜哄开心',
  '清爽｜健康｜刚刚好',
]

/** @param {string} budget */
export function budgetRange(budget) {
  if (budget === '50以内') return [0, 50]
  if (budget === '50-100') return [50, 100]
  if (budget === '100-200') return [100, 200]
  return [200, Infinity]
}

/** @param {Dish} dish @param {string[]} avoids */
export function matchesAvoid(dish, avoids) {
  if (avoids.includes('香菜') && (dish.tags.includes('含香菜') || dish.name.includes('香菜'))) return false
  if (avoids.includes('海鲜') && dish.tags.includes('含海鲜')) return false
  if (avoids.includes('太油') && dish.tags.includes('偏油')) return false
  if (avoids.includes('太辣') && (dish.spicy === 'hot' || dish.spicy === 'mild')) return false
  return true
}

/** @param {Dish} dish @param {string} taste */
export function matchesTaste(dish, taste) {
  if (taste === '清淡') return dish.spicy === 'none' || dish.tags.includes('清淡')
  if (taste === '微辣') return dish.spicy === 'none' || dish.spicy === 'mild'
  if (taste === '重辣') return dish.spicy === 'mild' || dish.spicy === 'hot'
  return true
}

/** @param {Dish} dish @param {string} scene */
export function sceneScore(dish, scene) {
  if (scene === '约会' && dish.tags.some((t) => ['约会', '浪漫'].includes(t))) return 3
  if (scene === '下班随便吃' && dish.tags.some((t) => ['快手', '下班随便吃', '不踩雷'].includes(t))) return 3
  if (scene === '周末改善伙食' && (dish.price >= 50 || dish.tags.includes('周末改善伙食'))) return 3
  if (scene === '哄女朋友开心' && dish.tags.includes('哄女朋友开心')) return 3
  return 1
}

/** @param {Dish[]} pool */
export function pickRandom(pool) {
  if (!pool.length) return null
  return pool[Math.floor(Math.random() * pool.length)]
}

/** @param {Dish[]} pool @param {string} scene */
export function pickWeighted(pool, scene) {
  if (!pool.length) return null
  const weights = pool.map((d) => sceneScore(d, scene))
  const total = weights.reduce((a, b) => a + b, 0)
  let r = Math.random() * total
  for (let i = 0; i < pool.length; i += 1) {
    r -= weights[i]
    if (r <= 0) return pool[i]
  }
  return pool[pool.length - 1]
}

/** @param {Dish[]} dishes */
export function calcSpicyLabel(dishes) {
  const levels = dishes.map((d) => d.spicy)
  if (levels.includes('hot')) return '偏辣'
  if (levels.includes('mild')) return '微辣'
  return '清淡'
}

/** @param {Dish[]} dishes */
export function calcStars(dishes) {
  const avg = dishes.reduce((s, d) => s + d.price, 0) / dishes.length
  if (avg >= 60) return 5
  if (avg >= 40) return 4
  if (avg >= 25) return 3
  return 2
}
