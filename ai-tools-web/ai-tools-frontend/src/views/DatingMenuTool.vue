<script setup>
import { computed, ref } from 'vue'
import { RouterLink } from 'vue-router'
import {
  AVOID_OPTIONS,
  BUDGET_OPTIONS,
  CATEGORY_FILTERS,
  CATEGORY_META,
  CUISINE_FILTERS,
  DISHES,
  KEYWORD_POOL,
  SCENE_OPTIONS,
  TAGLINES,
  TASTE_OPTIONS,
  budgetRange,
  calcSpicyLabel,
  calcStars,
  matchesAvoid,
  matchesTaste,
  pickWeighted,
} from '../data/datingMenuDishes.js'
import './DatingMenuTool.css'

const mode = ref('recommend')
const taste = ref('微辣')
const scene = ref('约会')
const budget = ref('50-100')
const avoids = ref([])

const cuisineFilter = ref('全部')
const categoryFilter = ref('全部')
const selectedIds = ref([])

const menuResult = ref(null)
const toast = ref('')

const ORDERED_CATEGORIES = ['主菜', '肉菜', '素菜', '主食', '饮品', '甜品']

const filteredDishes = computed(() =>
  DISHES.filter((d) => {
    if (cuisineFilter.value !== '全部' && d.cuisine !== cuisineFilter.value) return false
    if (categoryFilter.value !== '全部' && d.category !== categoryFilter.value) return false
    return true
  }),
)

const selectedCount = computed(() => selectedIds.value.length)

function showToast(msg) {
  toast.value = msg
  window.setTimeout(() => {
    toast.value = ''
  }, 2200)
}

function toggleAvoid(item) {
  if (avoids.value.includes(item)) {
    avoids.value = avoids.value.filter((a) => a !== item)
  } else {
    avoids.value = [...avoids.value, item]
  }
}

function toggleDish(id) {
  if (selectedIds.value.includes(id)) {
    selectedIds.value = selectedIds.value.filter((x) => x !== id)
  } else {
    selectedIds.value = [...selectedIds.value, id]
  }
}

function clearSelection() {
  selectedIds.value = []
  showToast('已清空选择')
}

function randomFrom(arr) {
  return arr[Math.floor(Math.random() * arr.length)]
}

function buildMenuCard(dishes) {
  const total = dishes.reduce((s, d) => s + d.price, 0)
  const stars = calcStars(dishes)
  return {
    dishes,
    tagline: randomFrom(TAGLINES),
    keywords: randomFrom(KEYWORD_POOL),
    total,
    spicyLabel: calcSpicyLabel(dishes),
    stars: '⭐'.repeat(stars),
  }
}

function groupByCategory(dishes) {
  return ORDERED_CATEGORIES.map((cat) => ({
    category: cat,
    ...CATEGORY_META[cat],
    items: dishes.filter((d) => d.category === cat),
  })).filter((g) => g.items.length > 0)
}

function filterPool(category) {
  return DISHES.filter((d) => {
    if (d.category !== category) return false
    if (!matchesAvoid(d, avoids.value)) return false
    if (!matchesTaste(d, taste.value)) return false
    return true
  })
}

function generateRecommendMenu() {
  const [minBudget, maxBudget] = budgetRange(budget.value)
  const includeDessert = Math.random() > 0.35
  const required = ['主菜', '肉菜', '素菜', '主食', '饮品']
  if (includeDessert) required.push('甜品')

  for (let attempt = 0; attempt < 80; attempt += 1) {
    const picked = []
    for (const cat of required) {
      const pool = filterPool(cat)
      const dish = pickWeighted(pool, scene.value)
      if (!dish) break
      picked.push(dish)
    }
    if (picked.length !== required.length) continue

    const total = picked.reduce((s, d) => s + d.price, 0)
    if (total < minBudget || total > maxBudget) continue

    menuResult.value = buildMenuCard(picked)
    return
  }

  const fallback = []
  for (const cat of required) {
    const pool = filterPool(cat)
    const dish = pickWeighted(pool, scene.value)
    if (dish) fallback.push(dish)
  }
  if (fallback.length < 4) {
    showToast('条件太严格啦，试试放宽忌口或预算')
    return
  }
  menuResult.value = buildMenuCard(fallback)
}

function generateCustomMenu() {
  if (!selectedIds.value.length) {
    showToast('先选几个菜再生成菜单哦')
    return
  }
  const dishes = DISHES.filter((d) => selectedIds.value.includes(d.id))
  menuResult.value = buildMenuCard(dishes)
}

function regenerateMenu() {
  if (mode.value === 'recommend') {
    generateRecommendMenu()
  } else {
    generateCustomMenu()
  }
}

const groupedResult = computed(() =>
  menuResult.value ? groupByCategory(menuResult.value.dishes) : [],
)
</script>

<template>
  <div class="dating-menu-page">
    <div class="dating-menu-shell">
      <nav class="dating-menu-nav">
        <RouterLink to="/">← 首页</RouterLink>
      </nav>

      <header class="dating-menu-header">
        <h1>💖 情侣点菜助手</h1>
        <p>不知道吃什么？帮你生成一份好看的今日菜单</p>
      </header>

      <div class="dating-menu-tabs">
        <button
          type="button"
          class="dating-menu-tab"
          :class="{ active: mode === 'recommend' }"
          @click="mode = 'recommend'"
        >
          智能推荐
        </button>
        <button
          type="button"
          class="dating-menu-tab"
          :class="{ active: mode === 'custom' }"
          @click="mode = 'custom'"
        >
          自己点菜
        </button>
      </div>

      <!-- 智能推荐 -->
      <section v-if="mode === 'recommend'" class="dating-menu-panel">
        <div class="dating-menu-field">
          <label>口味</label>
          <div class="dating-menu-chips">
            <button
              v-for="opt in TASTE_OPTIONS"
              :key="opt"
              type="button"
              class="dating-menu-chip"
              :class="{ active: taste === opt }"
              @click="taste = opt"
            >
              {{ opt }}
            </button>
          </div>
        </div>

        <div class="dating-menu-field">
          <label>场景</label>
          <div class="dating-menu-chips">
            <button
              v-for="opt in SCENE_OPTIONS"
              :key="opt"
              type="button"
              class="dating-menu-chip"
              :class="{ active: scene === opt }"
              @click="scene = opt"
            >
              {{ opt }}
            </button>
          </div>
        </div>

        <div class="dating-menu-field">
          <label>预算</label>
          <div class="dating-menu-chips">
            <button
              v-for="opt in BUDGET_OPTIONS"
              :key="opt"
              type="button"
              class="dating-menu-chip"
              :class="{ active: budget === opt }"
              @click="budget = opt"
            >
              {{ opt }}
            </button>
          </div>
        </div>

        <div class="dating-menu-field">
          <label>忌口（可多选）</label>
          <div class="dating-menu-chips">
            <button
              v-for="opt in AVOID_OPTIONS"
              :key="opt"
              type="button"
              class="dating-menu-chip"
              :class="{ active: avoids.includes(opt) }"
              @click="toggleAvoid(opt)"
            >
              {{ opt }}
            </button>
          </div>
        </div>

        <button type="button" class="dating-menu-btn" @click="generateRecommendMenu">
          生成今日菜单
        </button>
      </section>

      <!-- 自己点菜 -->
      <section v-else class="dating-menu-panel">
        <div class="dating-menu-filters">
          <div class="dating-menu-filter-row">
            <button
              v-for="c in CUISINE_FILTERS"
              :key="c"
              type="button"
              class="dating-menu-filter-chip"
              :class="{ active: cuisineFilter === c }"
              @click="cuisineFilter = c"
            >
              {{ c }}
            </button>
          </div>
          <div class="dating-menu-filter-row">
            <button
              v-for="c in CATEGORY_FILTERS"
              :key="c"
              type="button"
              class="dating-menu-filter-chip"
              :class="{ active: categoryFilter === c }"
              @click="categoryFilter = c"
            >
              {{ c }}
            </button>
          </div>
        </div>

        <div v-if="filteredDishes.length" class="dating-menu-dish-list">
          <button
            v-for="dish in filteredDishes"
            :key="dish.id"
            type="button"
            class="dating-menu-dish-card"
            :class="{ selected: selectedIds.includes(dish.id) }"
            @click="toggleDish(dish.id)"
          >
            <span class="dating-menu-dish-emoji">{{ dish.emoji }}</span>
            <div class="dating-menu-dish-body">
              <div class="dating-menu-dish-name">{{ dish.name }}</div>
              <div class="dating-menu-dish-meta">{{ dish.cuisine }} · {{ dish.category }}</div>
              <div class="dating-menu-dish-tags">
                <span v-for="tag in dish.tags.slice(0, 3)" :key="tag" class="dating-menu-tag">
                  {{ tag }}
                </span>
              </div>
            </div>
            <span class="dating-menu-dish-price">¥{{ dish.price }}</span>
            <span class="dating-menu-dish-check">✓</span>
          </button>
        </div>
        <div v-else class="dating-menu-empty">暂无符合条件的菜品</div>

        <div class="dating-menu-selected-bar">
          <span>已选 <strong>{{ selectedCount }}</strong> 道菜</span>
          <button type="button" class="dating-menu-clear" @click="clearSelection">
            清空选择
          </button>
        </div>

        <button type="button" class="dating-menu-btn" @click="generateCustomMenu">
          生成好看的菜单
        </button>
      </section>

      <!-- 菜单卡片 -->
      <section v-if="menuResult" class="dating-menu-result-wrap">
        <div class="dating-menu-result-actions">
          <button type="button" class="dating-menu-btn secondary" @click="regenerateMenu">
            重新生成
          </button>
        </div>

        <div class="dating-menu-card" id="dating-menu-screenshot">
          <div class="dating-menu-card-inner">
            <h2 class="dating-menu-card-title">💖 今日女友专属菜单</h2>
            <p class="dating-menu-card-tagline">{{ menuResult.tagline }}</p>

            <div
              v-for="group in groupedResult"
              :key="group.category"
              class="dating-menu-card-section"
            >
              <div class="dating-menu-card-section-title">
                {{ group.emoji }} {{ group.label }}
              </div>
              <div v-for="item in group.items" :key="item.id" class="dating-menu-card-item">
                <span class="dating-menu-card-item-emoji">{{ item.emoji }}</span>
                <div class="dating-menu-card-item-info">
                  <div class="dating-menu-card-item-name">{{ item.name }}</div>
                  <div class="dating-menu-card-item-tags">
                    <span v-for="tag in item.tags.slice(0, 2)" :key="tag" class="dating-menu-tag">
                      {{ tag }}
                    </span>
                  </div>
                </div>
                <span class="dating-menu-card-item-price">¥{{ item.price }}</span>
              </div>
            </div>

            <div class="dating-menu-card-footer">
              <div class="dating-menu-card-stat">
                <span>预算合计</span>
                <strong>约 ¥{{ menuResult.total }}</strong>
              </div>
              <div class="dating-menu-card-stat">
                <span>辣度</span>
                <strong>{{ menuResult.spicyLabel }}</strong>
              </div>
              <div class="dating-menu-card-stat">
                <span>今日关键词</span>
                <strong>{{ menuResult.keywords }}</strong>
              </div>
              <div class="dating-menu-card-stars">
                推荐指数：{{ menuResult.stars }}
              </div>
            </div>
          </div>
        </div>
      </section>
    </div>

    <div v-if="toast" class="dating-menu-toast">{{ toast }}</div>
  </div>
</template>
