<script setup>
defineProps({
  preview: { type: Object, required: true },
})
</script>

<template>
  <section class="preview-hero" :class="{ 'preview-hero--active': !preview.isForming }" aria-live="polite">
    <h2 class="preview-hero__title">{{ preview.title }}</h2>
    <p class="preview-hero__sub">{{ preview.subtitle }}</p>

    <div class="preview-hero__body">
      <div class="preview-item">
        <span class="preview-item__label">当前人生方向</span>
        <p class="preview-item__value">{{ preview.lifeDirection }}</p>
      </div>
      <div class="preview-item">
        <span class="preview-item__label">当前倾向</span>
        <ul v-if="preview.tendencies?.length" class="preview-tags">
          <li v-for="tag in preview.tendencies" :key="tag">{{ tag }}</li>
        </ul>
      </div>
      <div class="preview-item">
        <span class="preview-item__label">AI 理解中的人格路线</span>
        <p class="preview-item__personality">{{ preview.personalityRoute }}</p>
      </div>
      <div class="preview-item preview-item--world">
        <span class="preview-item__label">路线走向</span>
        <p class="preview-item__world">{{ preview.worldLine }}</p>
      </div>
    </div>
  </section>
</template>
