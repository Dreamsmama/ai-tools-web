<script setup>
import { ref } from 'vue'
import { RouterLink, useRouter } from 'vue-router'
import { API, apiUrl, logApiFailure } from '../api.js'
import {
  httpErrorMessage,
  NETWORK_UNREACHABLE,
  RESPONSE_PARSE_ERROR,
} from '../clientErrors.js'
import ErrorDialog from '../components/ErrorDialog.vue'

const STORAGE_KEY = 'consult_result'

const router = useRouter()
const symptom = ref('')
const report = ref('')
const target = ref('')
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

async function onGenerate() {
  if (loading.value) return

  const s = (symptom.value || '').trim()
  const r = (report.value || '').trim()
  const t = (target.value || '').trim()

  if (!s || s.length < 3) {
    showToast('请尽量详细描述症状（至少一句话）')
    return
  }

  loading.value = true
  const url = apiUrl(API.medicalAssistant)
  const requestBody = {
    symptom: s,
    report: r,
    target: t,
  }
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

    let payload
    try {
      payload = await res.json()
    } catch (parseErr) {
      await logApiFailure(url, requestBody, res, parseErr)
      showErrorDetail(RESPONSE_PARSE_ERROR)
      return
    }

    if (!payload || payload.code !== 0) {
      console.error('[medical-assistant business]', {
        url,
        code: payload?.code,
        message: payload?.message,
        payload,
      })
      showErrorDetail(
        payload?.message ||
          '【原因】本次未成功。\n【怎么办】无需改内容，直接再点一次提交试试，通常 1～2 次就会好。',
      )
      return
    }

    try {
      sessionStorage.setItem(STORAGE_KEY, JSON.stringify(payload.data))
    } catch (e) {
      console.error(e)
      showToast('无法保存结果，请检查浏览器存储')
      return
    }

    router.push({ name: 'medicalResult' })
  } catch (e) {
    await logApiFailure(url, requestBody, null, e)
    showErrorDetail(NETWORK_UNREACHABLE)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="page">
    <header class="nav">
      <RouterLink class="back" to="/">← 首页</RouterLink>
    </header>

    <section class="card">
      <h1 class="title">问诊准备</h1>
      <p class="sub">把你现在的情况写清楚，系统会帮你整理成就医沟通清单。</p>
    </section>

    <section class="card">
      <div class="label">1）现在的情况 / 不舒服的地方（必填）</div>
      <textarea
        v-model="symptom"
        class="textarea"
        maxlength="800"
        rows="8"
        placeholder="建议按这个模板写（越具体越有用）：
- 部位：上腹/下腹/左/右？
- 性质：绞痛/胀痛/隐痛？
- 时长：多久了？有没有加重？
- 诱因：饭后/受凉/熬夜/运动？
- 伴随：发热/腹泻/恶心/便血？
示例：右下腹隐痛2天，走路更痛，偶尔恶心，无发热。"
      />
      <p class="hint">写得越具体，生成的清单越有用。</p>
    </section>

    <section class="card">
      <div class="label">2）已经做过的检查 / 报告（可选）</div>
      <textarea
        v-model="report"
        class="textarea"
        maxlength="800"
        rows="5"
        placeholder="可填写：体检异常项、化验结果、影像检查结论、医生之前说法等。
示例：血常规白细胞略高；B超提示轻度脂肪肝。"
      />
    </section>

    <section class="card">
      <div class="label">3）你最想问医生的问题（可选）</div>
      <textarea
        v-model="target"
        class="textarea"
        maxlength="500"
        rows="5"
        placeholder="示例：
- 我最担心的是不是需要进一步检查？
- 我应该优先排查哪些方向？
- 哪些情况算需要尽快处理？"
      />
    </section>

    <p class="disclaimer-inline">
      ⚠️ 本工具仅用于健康信息整理与沟通准备，不构成医疗建议。
    </p>

    <button
      type="button"
      class="btn btn-gradient"
      :disabled="loading"
      @click="onGenerate"
    >
      {{ loading ? '生成中…' : '生成问诊准备' }}
    </button>

    <div v-if="toast" class="toast" role="status">{{ toast }}</div>

    <ErrorDialog v-model="errorDialog" :text="errorText" />
  </div>
</template>

<style scoped>
.page {
  max-width: 720px;
  margin: 0 auto;
  padding: 16px 12px 40px;
  min-height: 100vh;
}

.nav {
  padding: 4px 4px 14px;
}

.back {
  font-size: 14px;
  font-weight: 500;
  color: #6366f1;
  text-decoration: none;
}

.back:hover {
  opacity: 0.85;
}

.card {
  background: rgba(255, 255, 255, 0.88);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  border-radius: 18px;
  padding: 18px 16px;
  margin-bottom: 14px;
  border: 1px solid rgba(148, 163, 184, 0.22);
  box-shadow: 0 4px 24px rgba(15, 23, 42, 0.06);
}

.title {
  font-size: 21px;
  font-weight: 800;
  letter-spacing: -0.02em;
  margin: 0 0 8px;
  background: linear-gradient(135deg, #0f172a, #4338ca);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.sub {
  margin: 0;
  font-size: 14px;
  color: #64748b;
  line-height: 1.55;
}

.label {
  font-size: 13px;
  font-weight: 600;
  color: #475569;
  margin-bottom: 10px;
}

.textarea {
  width: 100%;
  min-height: 120px;
  padding: 14px;
  border-radius: 14px;
  background: rgba(241, 245, 249, 0.9);
  border: 1px solid rgba(148, 163, 184, 0.22);
  font-size: 15px;
  line-height: 1.55;
  resize: vertical;
  transition:
    border-color 0.2s,
    box-shadow 0.2s;
}

.textarea:focus {
  outline: none;
  border-color: rgba(99, 102, 241, 0.45);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.12);
}

.hint {
  font-size: 13px;
  color: #94a3b8;
  margin: 8px 0 0;
}

.disclaimer-inline {
  margin: 0 4px 14px;
  padding: 12px 14px;
  border-radius: 14px;
  background: linear-gradient(135deg, rgba(254, 243, 199, 0.55), rgba(255, 237, 213, 0.45));
  color: #92400e;
  font-size: 12px;
  line-height: 1.55;
  border: 1px solid rgba(251, 191, 36, 0.3);
}

.btn {
  width: calc(100% - 8px);
  margin: 0 4px;
  padding: 14px 16px;
  border-radius: 14px;
  font-size: 16px;
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
  backdrop-filter: blur(8px);
  color: #fff;
  font-size: 14px;
  z-index: 2000;
  max-width: 90vw;
  text-align: center;
  box-shadow: 0 12px 40px rgba(15, 23, 42, 0.25);
}
</style>
