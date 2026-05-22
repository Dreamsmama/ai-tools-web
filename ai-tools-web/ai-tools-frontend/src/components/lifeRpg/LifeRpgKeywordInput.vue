<script setup>
import { ref } from 'vue'
import { MAX_LIFE_KEYWORDS, RECOMMENDED_KEYWORDS } from '../../data/lifeRpgOptions.js'

const props = defineProps({
  modelValue: { type: Array, default: () => [] },
})

const emit = defineEmits(['update:modelValue'])

const draft = ref('')

function emitTags(tags) {
  emit('update:modelValue', tags.slice(0, MAX_LIFE_KEYWORDS))
}

function addTag(raw) {
  const tag = (raw || '').trim().replace(/[,，、\s]+/g, '')
  if (!tag) return
  const list = [...props.modelValue]
  if (list.includes(tag) || list.length >= MAX_LIFE_KEYWORDS) return
  emitTags([...list, tag])
  draft.value = ''
}

function removeTag(tag) {
  emitTags(props.modelValue.filter((t) => t !== tag))
}

function onKeydown(e) {
  if (e.key === 'Enter') {
    e.preventDefault()
    addTag(draft.value)
  }
}

function pickRecommended(tag) {
  addTag(tag)
}
</script>

<template>
  <div class="kw-box">
    <div v-if="modelValue.length" class="kw-tags" role="list">
      <span v-for="tag in modelValue" :key="tag" class="kw-tag" role="listitem">
        {{ tag }}
        <button type="button" class="kw-tag-remove" aria-label="移除" @click="removeTag(tag)">×</button>
      </span>
    </div>
    <input
      v-model="draft"
      class="text-input kw-input"
      type="text"
      :placeholder="modelValue.length >= MAX_LIFE_KEYWORDS ? '已达 5 个关键词' : '输入后按回车添加'"
      :disabled="modelValue.length >= MAX_LIFE_KEYWORDS"
      @keydown="onKeydown"
      @blur="addTag(draft)"
    />
    <p class="kw-limit">{{ modelValue.length }} / {{ MAX_LIFE_KEYWORDS }}</p>
    <p class="kw-rec-label">推荐关键词</p>
    <div class="chip-grid">
      <button
        v-for="tag in RECOMMENDED_KEYWORDS"
        :key="tag"
        type="button"
        class="chip chip--suggest"
        :class="{ selected: modelValue.includes(tag) }"
        :disabled="!modelValue.includes(tag) && modelValue.length >= MAX_LIFE_KEYWORDS"
        @click="pickRecommended(tag)"
      >
        {{ tag }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.kw-box {
  width: 100%;
}

.kw-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-bottom: 10px;
}

.kw-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 13px;
  font-weight: 600;
  color: var(--accent-a);
  background: rgba(238, 242, 255, 0.95);
  border: 1px solid rgba(99, 102, 241, 0.2);
}

.kw-tag-remove {
  border: none;
  background: transparent;
  color: var(--text-muted);
  font-size: 16px;
  line-height: 1;
  padding: 0 2px;
}

.kw-limit {
  margin: 6px 0 10px;
  text-align: right;
  font-size: 12px;
  color: var(--text-muted);
}

.kw-rec-label {
  margin: 0 0 8px;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
}

.chip--suggest {
  font-size: 13px;
  padding: 8px 12px;
}

.chip--suggest:disabled:not(.selected) {
  opacity: 0.45;
}
</style>
