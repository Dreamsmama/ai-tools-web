<script setup>
import { computed, ref } from 'vue'
import {
  DIRECTION_TEMPLATES,
  LIFE_STATE_OPTIONS,
  validateCharacterForm,
} from '../../data/lifeRpgOptions.js'
import { buildCharacterPreview } from '../../lib/lifeRpgCharacterPreview.js'
import IdentityOccupationPicker from './IdentityOccupationPicker.vue'
import LifeRpgCharacterPreviewCard from './LifeRpgCharacterPreviewCard.vue'
import LifeRpgKeywordInput from './LifeRpgKeywordInput.vue'

const props = defineProps({
  modelValue: { type: Object, required: true },
  loading: { type: Boolean, default: false },
  editMode: { type: Boolean, default: false },
})

const emit = defineEmits(['update:modelValue', 'submit', 'invalid'])

const notesOpen = ref(!!(props.modelValue.custom_notes || '').trim())
const preview = computed(() => buildCharacterPreview(props.modelValue))

function patch(partial) {
  emit('update:modelValue', { ...props.modelValue, ...partial })
}

function toggleLifeState(label) {
  const list = [...(props.modelValue.life_states || [])]
  const idx = list.indexOf(label)
  if (idx >= 0) list.splice(idx, 1)
  else list.push(label)
  patch({ life_states: list })
}

function isStateSelected(label) {
  return (props.modelValue.life_states || []).includes(label)
}

function selectTemplate(id) {
  patch({ direction_template: id })
}

function onSubmit() {
  const v = validateCharacterForm(props.modelValue)
  if (!v.ok) {
    emit('invalid', v.message)
    return
  }
  emit('submit')
}
</script>

<template>
  <form class="create-form" @submit.prevent="onSubmit">
    <LifeRpgCharacterPreviewCard :preview="preview" />

    <section class="tool-card">
      <p class="field-label">你最近更想靠近怎样的人生状态？</p>
      <p class="field-desc">选择你最近真正想靠近的状态，AI 会帮你规划成长路线。</p>
      <div class="state-grid" role="group" aria-label="人生状态">
        <button
          v-for="opt in LIFE_STATE_OPTIONS"
          :key="opt"
          type="button"
          class="state-card"
          :class="{ selected: isStateSelected(opt) }"
          :aria-pressed="isStateSelected(opt)"
          @click="toggleLifeState(opt)"
        >
          {{ opt }}
        </button>
      </div>
      <input
        v-if="isStateSelected('自定义')"
        class="text-input state-custom"
        type="text"
        placeholder="用一句话描述你的状态"
        :value="modelValue.custom_life_state"
        @input="patch({ custom_life_state: ($event.target).value })"
      />
    </section>

    <section class="tool-card">
      <p class="field-label">你最近想推进什么方向？</p>
      <p class="field-desc">不知道怎么开始？可以先选一个人生方向模板。</p>
      <div class="template-list" role="radiogroup" aria-label="人生方向模板">
        <button
          v-for="tpl in DIRECTION_TEMPLATES"
          :key="tpl.id"
          type="button"
          class="template-card"
          :class="{ selected: modelValue.direction_template === tpl.id }"
          role="radio"
          :aria-checked="modelValue.direction_template === tpl.id"
          @click="selectTemplate(tpl.id)"
        >
          <span class="template-card__title">{{ tpl.title }}</span>
          <span class="template-card__sub">{{ tpl.subtitle }}</span>
          <span class="template-card__examples">{{ tpl.examples.join(' · ') }}</span>
        </button>
      </div>
    </section>

    <section class="tool-card">
      <p class="field-label">你的人生关键词</p>
      <p class="field-desc">这些关键词将成为你人生路线的核心方向。</p>
      <LifeRpgKeywordInput
        :model-value="modelValue.life_keywords"
        @update:model-value="patch({ life_keywords: $event })"
      />
    </section>

    <section class="tool-card tool-card--fold">
      <button type="button" class="fold-trigger" @click="notesOpen = !notesOpen">
        <span class="field-label fold-trigger__label">AI 更了解你 <span class="hint">可选</span></span>
        <span class="fold-trigger__action">{{ notesOpen ? '收起' : '补充一点最近的想法' }}</span>
      </button>
      <div v-show="notesOpen" class="fold-body">
        <textarea
          id="life-rpg-notes"
          class="textarea"
          rows="4"
          placeholder="例如：&#10;- 最近精神有点累，想恢复规律生活&#10;- 想认真学习 AI 开发&#10;- 想减少刷手机&#10;- 想重新培养长期兴趣"
          :value="modelValue.custom_notes"
          @input="patch({ custom_notes: ($event.target).value })"
        />
      </div>
    </section>

    <section class="tool-card">
      <p class="field-label">你此刻所处的位置 <span class="hint">可选</span></p>
      <IdentityOccupationPicker
        :model-value="{
          identity_type: modelValue.identity_type,
          occupation: modelValue.occupation,
        }"
        @update:model-value="
          patch({
            identity_type: $event.identity_type,
            occupation: $event.occupation,
          })
        "
      />
    </section>

    <button type="submit" class="btn btn-gradient submit-btn" :disabled="loading">
      {{
        loading
          ? 'AI 正在生成你的人生路线…'
          : editMode
            ? '更新人生角色'
            : '生成我的人生路线'
      }}
    </button>
  </form>
</template>

<style scoped>
.create-form {
  display: flex;
  flex-direction: column;
}

.state-custom {
  margin-top: 10px;
}

.fold-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  width: 100%;
  padding: 0;
  border: none;
  background: transparent;
  text-align: left;
}

.fold-trigger__label {
  margin: 0;
}

.fold-trigger__action {
  flex-shrink: 0;
  font-size: 13px;
  font-weight: 600;
  color: var(--accent-a);
}

.fold-body {
  margin-top: 12px;
}
</style>
