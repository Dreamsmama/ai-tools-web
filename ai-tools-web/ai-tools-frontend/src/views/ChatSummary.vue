<script setup>
import { ref } from 'vue'
import { RouterLink } from 'vue-router'
import { API, apiUrl, logApiFailure } from '../api.js'
import {
  httpErrorMessage,
  NETWORK_UNREACHABLE,
  RESPONSE_PARSE_ERROR,
} from '../clientErrors.js'
import ErrorDialog from '../components/ErrorDialog.vue'

const STORAGE_KEY = 'summary_used_count'

const inputText = ref('')
const result = ref(null)
const showUnlockModal = ref(false)
const loading = ref(false)
const toast = ref('')
const errorDialog = ref(false)
const errorText = ref('')

function showErrorDetail(text) {
  errorText.value = text
  errorDialog.value = true
}

function showToast(message) {
  toast.value = message
  window.setTimeout(() => {
    toast.value = ''
  }, 2200)
}

function getSummaryCount() {
  try {
    const v = localStorage.getItem(STORAGE_KEY)
    return v ? parseInt(v, 10) || 0 : 0
  } catch {
    return 0
  }
}

function incrementSummaryCount() {
  const n = getSummaryCount() + 1
  try {
    localStorage.setItem(STORAGE_KEY, String(n))
  } catch {
    /* ignore */
  }
}

function checkUnlock() {
  if (getSummaryCount() >= 3) {
    showUnlockModal.value = true
    return true
  }
  return false
}

function onCloseUnlockModal() {
  showUnlockModal.value = false
}

function onUnlockClick() {
  showToast('功能开发中')
  showUnlockModal.value = false
}

async function onSummarize() {
  const text = (inputText.value || '').trim()
  if (!text) {
    showToast('先粘贴聊天内容')
    return
  }

  checkUnlock()

  loading.value = true
  const url = apiUrl(API.summary)
  const requestBody = { inputText: text }
  try {
    const res = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(requestBody),
    })

    if (!res.ok) {
      await logApiFailure(url, requestBody, res, new Error(`HTTP ${res.status}`))
      showErrorDetail(httpErrorMessage(res.status))
      return
    }

    let r
    try {
      r = await res.json()
    } catch (parseErr) {
      await logApiFailure(url, requestBody, res, parseErr)
      showErrorDetail(RESPONSE_PARSE_ERROR)
      return
    }

    if (r?.code !== 0) {
      console.error('[summary business]', { url, code: r?.code, message: r?.message, data: r })
      showErrorDetail(
        r?.message ||
          '【原因】本次未成功。\n【怎么办】无需改内容，直接再点一次提交试试，通常 1～2 次就会好。',
      )
      return
    }

    incrementSummaryCount()
    result.value = r.data ?? null
  } catch (e) {
    await logApiFailure(url, requestBody, null, e)
    showErrorDetail(NETWORK_UNREACHABLE)
  } finally {
    loading.value = false
  }
}

async function copyReply() {
  const reply = result.value?.reply
  if (!reply) return
  try {
    await navigator.clipboard.writeText(reply)
    showToast('已复制')
  } catch {
    showToast('复制失败，请手动选择复制')
  }
}
</script>

<template>
  <div class="page">
    <nav class="top-nav">
      <RouterLink class="nav-link" to="/">← 首页</RouterLink>
    </nav>
    <header class="header">
      <h1 class="title">聊天重点总结器（内测）</h1>
      <p class="sub">粘贴聊天内容 → 输出结论 / 待办 / 风险</p>
    </header>

    <section class="card">
      <div class="label">粘贴聊天内容</div>
      <textarea
        v-model="inputText"
        class="textarea"
        placeholder="把微信/群聊/工作对话粘贴到这里…（支持多段文字）"
        rows="10"
        spellcheck="false"
      />
      <button
        type="button"
        class="btn btn-gradient"
        :disabled="loading"
        @click="onSummarize"
      >
        {{ loading ? '总结中…' : '一键总结' }}
      </button>
    </section>

    <section class="card">
      <h2 class="block-title">核心结论</h2>
      <template v-if="!result">
        <p class="empty">点击「一键总结」后显示</p>
      </template>
      <template v-else>
        <p
          v-for="(item, idx) in result.summary"
          :key="'s-' + idx"
          class="item"
        >
          • {{ item }}
        </p>
      </template>
    </section>

    <section class="card">
      <h2 class="block-title">待办事项</h2>
      <template v-if="!result">
        <p class="empty">点击「一键总结」后显示</p>
      </template>
      <template v-else>
        <p
          v-for="(item, idx) in result.todos"
          :key="'t-' + idx"
          class="item"
        >
          • {{ item.owner }}：{{ item.task }}
        </p>
      </template>
    </section>

    <section class="card">
      <h2 class="block-title">风险 / 没说清的地方</h2>
      <template v-if="!result">
        <p class="empty">点击「一键总结」后显示</p>
      </template>
      <template v-else>
        <p
          v-for="(item, idx) in result.risks"
          :key="'r-' + idx"
          class="item"
        >
          • {{ item }}
        </p>
      </template>
    </section>

    <section class="card">
      <h2 class="block-title">建议下一步怎么回</h2>
      <template v-if="!result">
        <p class="empty">点击「一键总结」后显示</p>
      </template>
      <template v-else>
        <div class="reply">{{ result.reply }}</div>
        <button type="button" class="copyBtn" @click="copyReply">
          复制这段回复
        </button>
      </template>
    </section>

    <div v-if="toast" class="toast" role="status">{{ toast }}</div>

    <div
      v-if="showUnlockModal"
      class="unlock-modal-mask"
      @click.self="onCloseUnlockModal"
    >
      <div class="unlock-modal" @click.stop>
        <div class="unlock-modal-title">解锁更多使用次数</div>
        <p class="unlock-modal-content">
          你已经使用了 3
          次聊天总结，如果这个工具对你有帮助，可以支持一下我们继续完善
        </p>
        <div class="unlock-modal-buttons">
          <button
            type="button"
            class="unlock-btn-secondary"
            @click="onCloseUnlockModal"
          >
            以后再说
          </button>
          <button
            type="button"
            class="unlock-btn-primary"
            @click="onUnlockClick"
          >
            解锁更多
          </button>
        </div>
      </div>
    </div>

    <ErrorDialog v-model="errorDialog" :text="errorText" />
  </div>
</template>

<style scoped>
.page {
  padding: 16px 12px 40px;
  max-width: 720px;
  margin: 0 auto;
  min-height: 100vh;
}

.top-nav {
  padding: 0 4px 12px;
}

.nav-link {
  font-size: 14px;
  font-weight: 500;
  color: #6366f1;
  text-decoration: none;
  transition: opacity 0.2s;
}

.nav-link:hover {
  opacity: 0.8;
}

.header {
  margin-bottom: 18px;
  padding: 4px 4px 0;
}

.title {
  font-size: 22px;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin: 0;
  line-height: 1.3;
  background: linear-gradient(135deg, #0f172a 0%, #4338ca 45%, #7c3aed 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.sub {
  margin: 10px 0 0;
  font-size: 14px;
  color: var(--text-muted, #64748b);
  line-height: 1.55;
}

.card {
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-radius: var(--radius, 18px);
  padding: 18px 16px;
  margin-bottom: 14px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  box-shadow: var(--shadow-card, 0 4px 24px rgba(15, 23, 42, 0.06));
}

.label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 10px;
}

.textarea {
  width: 100%;
  min-height: 160px;
  padding: 14px;
  border-radius: 14px;
  background: rgba(241, 245, 249, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.22);
  font-size: 15px;
  color: #0f172a;
  resize: vertical;
  line-height: 1.55;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}

.textarea:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.45);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

.btn {
  width: 100%;
  margin-top: 14px;
  padding: 14px 16px;
  border-radius: 14px;
  font-size: 16px;
  font-weight: 600;
  text-align: center;
}

.block-title {
  font-size: 15px;
  font-weight: 700;
  margin: 0 0 12px;
  color: #0f172a;
  display: flex;
  align-items: center;
  gap: 8px;
}

.block-title::before {
  content: '';
  width: 4px;
  height: 1em;
  border-radius: 4px;
  background: linear-gradient(180deg, #6366f1, #a855f7);
}

.empty {
  font-size: 14px;
  color: #94a3b8;
  margin: 0;
}

.item {
  font-size: 15px;
  color: #334155;
  margin: 0 0 10px;
  line-height: 1.55;
  padding-left: 2px;
}

.item:last-child {
  margin-bottom: 0;
}

.reply {
  font-size: 15px;
  color: #1e293b;
  line-height: 1.65;
  padding: 14px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(241, 245, 249, 0.95), rgba(238, 242, 255, 0.9));
  border: 1px solid rgba(148, 163, 184, 0.22);
  white-space: pre-wrap;
  word-break: break-word;
}

.copyBtn {
  width: 100%;
  margin-top: 12px;
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid rgba(148, 163, 184, 0.35);
  background: rgba(255, 255, 255, 0.95);
  color: #4338ca;
  font-size: 15px;
  font-weight: 600;
  transition:
    background 0.2s,
    border-color 0.2s;
}

.copyBtn:hover {
  background: rgba(238, 242, 255, 0.9);
  border-color: rgba(99, 102, 241, 0.35);
}

.toast {
  position: fixed;
  left: 50%;
  bottom: 48px;
  transform: translateX(-50%);
  padding: 12px 20px;
  border-radius: 999px;
  background: rgba(15, 23, 42, 0.88);
  backdrop-filter: blur(8px);
  color: #fff;
  font-size: 14px;
  z-index: 2000;
  pointer-events: none;
  max-width: 90vw;
  text-align: center;
  box-shadow: 0 12px 40px rgba(15, 23, 42, 0.25);
}

.unlock-modal-mask {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.45);
  backdrop-filter: blur(6px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  padding: 16px;
}

.unlock-modal {
  width: 100%;
  max-width: 380px;
  background: rgba(255, 255, 255, 0.96);
  backdrop-filter: blur(16px);
  border-radius: 18px;
  padding: 26px 22px;
  border: 1px solid rgba(255, 255, 255, 0.8);
  box-shadow: 0 24px 60px rgba(15, 23, 42, 0.2);
}

.unlock-modal-title {
  font-size: 18px;
  font-weight: 700;
  color: #0f172a;
  text-align: center;
  margin-bottom: 14px;
}

.unlock-modal-content {
  font-size: 14px;
  color: #64748b;
  line-height: 1.65;
  text-align: center;
  margin: 0 0 22px;
}

.unlock-modal-buttons {
  display: flex;
  gap: 12px;
}

.unlock-btn-secondary {
  flex: 1;
  height: 46px;
  line-height: 46px;
  background: #f1f5f9;
  color: #475569;
  border: 1px solid rgba(148, 163, 184, 0.22);
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  padding: 0;
}

.unlock-btn-primary {
  flex: 1;
  height: 46px;
  line-height: 46px;
  border: none;
  border-radius: 12px;
  font-size: 14px;
  font-weight: 600;
  padding: 0;
  color: #fff;
  background: linear-gradient(135deg, #10b981, #059669);
  box-shadow: 0 8px 20px rgba(16, 185, 129, 0.35);
}
</style>
