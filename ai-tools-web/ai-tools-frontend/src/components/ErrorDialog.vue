<script setup>
defineProps({
  modelValue: { type: Boolean, default: false },
  title: { type: String, default: '出了一点问题' },
  text: { type: String, default: '' },
})

const emit = defineEmits(['update:modelValue'])

function close() {
  emit('update:modelValue', false)
}
</script>

<template>
  <div
    v-if="modelValue"
    class="mask"
    @click.self="close"
  >
    <div
      class="box"
      role="dialog"
      aria-modal="true"
      aria-labelledby="err-title"
    >
      <h3 id="err-title" class="title">{{ title }}</h3>
      <div class="body">{{ text }}</div>
      <button type="button" class="btn" @click="close">知道了</button>
    </div>
  </div>
</template>

<style scoped>
.mask {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 3000;
  padding: 20px;
}

.box {
  width: 100%;
  max-width: 400px;
  background: rgba(255, 255, 255, 0.98);
  border-radius: 16px;
  padding: 20px 18px;
  border: 1px solid rgba(148, 163, 184, 0.2);
  box-shadow: 0 20px 50px rgba(15, 23, 42, 0.2);
}

.title {
  margin: 0 0 12px;
  font-size: 17px;
  font-weight: 700;
  color: #0f172a;
}

.body {
  margin: 0 0 18px;
  font-size: 14px;
  line-height: 1.65;
  color: #475569;
  white-space: pre-line;
  word-break: break-word;
}

.btn {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 12px;
  font-size: 15px;
  font-weight: 600;
  color: #fff;
  background: linear-gradient(135deg, #6366f1, #8b5cf6);
  cursor: pointer;
}

.btn:hover {
  opacity: 0.95;
}
</style>
