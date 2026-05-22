<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import MaterialsManager from '../components/MaterialsManager.vue'
import ErrorDialog from '../../../components/ErrorDialog.vue'

const toastMsg = ref('')
const errorDialog = ref(false)
const errorText = ref('')

function showToast(message) {
  toastMsg.value = message
  window.setTimeout(() => {
    toastMsg.value = ''
  }, 2200)
}

function showError(text) {
  errorText.value = text
  errorDialog.value = true
}
</script>

<template>
  <header class="page-head card">
    <p class="kicker">Scene Materials</p>
    <h2 class="title">场景素材库</h2>
    <p class="sub">
      管理场景、界面、氛围等非人物素材。人物角色请在
      <RouterLink to="/tools/ai-short-drama/characters">角色管理</RouterLink>
      中配置。
    </p>
  </header>

  <MaterialsManager scene-only @toast="showToast" @error="showError" />

  <div v-if="toastMsg" class="toast" role="status">{{ toastMsg }}</div>
  <ErrorDialog v-model="errorDialog" :text="errorText" />
</template>

<style scoped>
.card {
  background: var(--surface-solid);
  border-radius: var(--radius);
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
}

.page-head {
  padding: 16px;
  margin-bottom: 14px;
}

.kicker {
  margin: 0 0 6px;
  font-size: 11px;
  font-weight: 700;
  color: #6366f1;
}

.title {
  margin: 0 0 6px;
  font-size: 18px;
  font-weight: 800;
}

.sub {
  margin: 0;
  font-size: 13px;
  line-height: 1.55;
  color: var(--text-muted);
}

.sub a {
  color: #4f46e5;
  font-weight: 600;
}

.toast {
  position: fixed;
  left: 50%;
  bottom: 48px;
  transform: translateX(-50%);
  padding: 12px 20px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.88);
  color: #fff;
  font-size: 14px;
  z-index: 2000;
}
</style>
