<script setup>
import CharacterIpWorkbench from '../components/CharacterIpWorkbench.vue'
import ErrorDialog from '../../../components/ErrorDialog.vue'
import { ref } from 'vue'

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
  <CharacterIpWorkbench @toast="showToast" @error="showError" />
  <div v-if="toastMsg" class="toast" role="status">{{ toastMsg }}</div>
  <ErrorDialog v-model="errorDialog" :text="errorText" />
</template>

<style scoped>
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
