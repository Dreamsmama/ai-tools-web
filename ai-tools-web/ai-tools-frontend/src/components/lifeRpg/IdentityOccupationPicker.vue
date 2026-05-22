<script setup>
import { computed, ref, watch } from 'vue'
import { IDENTITY_TYPE_OPTIONS } from '../../data/lifeRpgOptions.js'
import { searchOccupations } from '../../data/lifeRpgOccupations.js'

const props = defineProps({
  modelValue: { type: Object, required: true },
})

const emit = defineEmits(['update:modelValue'])

const query = ref(props.modelValue.occupation || '')
const dropdownOpen = ref(false)

const showOccupation = computed(
  () => props.modelValue.identity_type && props.modelValue.identity_type !== '暂不填写',
)

const suggestions = computed(() => {
  if (!showOccupation.value) return []
  return searchOccupations(query.value, 8)
})

function patch(partial) {
  const next = { ...props.modelValue, ...partial }
  emit('update:modelValue', next)
  if ('occupation' in partial) query.value = partial.occupation || ''
}

function onIdentityChange(e) {
  const type = e.target.value
  if (type === '暂不填写') {
    patch({ identity_type: type, occupation: '' })
    query.value = ''
    dropdownOpen.value = false
    return
  }
  patch({ identity_type: type })
}

function onOccupationInput(e) {
  const val = e.target.value
  query.value = val
  patch({ occupation: val })
  dropdownOpen.value = true
}

function pickOccupation(name) {
  query.value = name
  patch({ occupation: name })
  dropdownOpen.value = false
}

function onFocus() {
  if (showOccupation.value) dropdownOpen.value = true
}

function onBlur() {
  window.setTimeout(() => {
    dropdownOpen.value = false
  }, 180)
}

watch(
  () => props.modelValue.occupation,
  (v) => {
    if (v !== query.value) query.value = v || ''
  },
)
</script>

<template>
  <div class="identity-block">
    <div class="identity-row">
      <div class="field-col">
        <label class="field-label field-label--tight" for="life-rpg-identity-type">身份类型</label>
        <select
          id="life-rpg-identity-type"
          class="select-input"
          :value="modelValue.identity_type"
          @change="onIdentityChange"
        >
          <option value="" disabled>请选择</option>
          <option v-for="opt in IDENTITY_TYPE_OPTIONS" :key="opt" :value="opt">
            {{ opt }}
          </option>
        </select>
      </div>

      <div v-if="showOccupation" class="field-col">
        <label class="field-label field-label--tight" for="life-rpg-occupation">
          职业 <span class="hint">可选</span>
        </label>
        <div class="search-wrap">
          <input
            id="life-rpg-occupation"
            class="text-input search-input"
            type="search"
            autocomplete="off"
            placeholder="搜索职业"
            :value="query"
            @input="onOccupationInput"
            @focus="onFocus"
            @blur="onBlur"
          />
          <ul v-if="dropdownOpen && suggestions.length" class="suggest-list" role="listbox">
            <li
              v-for="item in suggestions"
              :key="item.name"
              role="option"
              class="suggest-item"
              @mousedown.prevent="pickOccupation(item.name)"
            >
              {{ item.name }}
            </li>
          </ul>
          <p v-else-if="dropdownOpen && query" class="suggest-empty">无匹配，可直接使用你输入的内容</p>
        </div>
      </div>
    </div>
    <p v-if="showOccupation" class="occ-hint">例如：前端 / 产品经理 / 医生 / HR</p>
  </div>
</template>
