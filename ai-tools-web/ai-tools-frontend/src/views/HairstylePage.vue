<script setup>
import { ref, onUnmounted } from 'vue'
import { RouterLink } from 'vue-router'
import { requestHairstyleGenerate } from '../lib/hairstyleApi.js'
import { staticUrl } from '../api.js'

const MALE_STYLES = ['韩系碎盖', '清爽短发', '三七分', '寸头', '商务背头', '微分碎盖']
const FEMALE_STYLES = ['锁骨发', '空气刘海', '法式短发', '韩系长卷发', '高层次长发', '温柔短发']

const BEAUTY_OPTIONS = [
  { value: 'natural', name: '自然真实', desc: '尽量只换发型，保留原图真实状态' },
  { value: 'light', name: '轻微美化', desc: '换发型 + 提亮肤色 + 优化光线，看起来更清爽自然' },
  { value: 'upgrade', name: '形象升级', desc: '换发型 + 更有精神感和气质，但仍保留本人特征' },
]

const imageUrl = ref('')
const imageFile = ref(null)
const gender = ref('female')
const selectedStyle = ref('')
const beautyLevel = ref('light')
const loading = ref(false)
const result = ref(null)
const errorMsg = ref('')

let objectUrl = ''

function handleFileChange(e) {
  const file = e.target.files?.[0]
  if (!file) return
  if (objectUrl) URL.revokeObjectURL(objectUrl)
  objectUrl = URL.createObjectURL(file)
  imageFile.value = file
  imageUrl.value = objectUrl
  result.value = null
  selectedStyle.value = ''
}

function resetUpload() {
  if (objectUrl) URL.revokeObjectURL(objectUrl)
  objectUrl = ''
  imageFile.value = null
  imageUrl.value = ''
  result.value = null
  errorMsg.value = ''
  selectedStyle.value = ''
  // Reset the input so same file can be re-selected
  const input = document.getElementById('hairstyle-photo')
  if (input) input.value = ''
}

function setGender(g) {
  gender.value = g
  selectedStyle.value = ''
}

function selectStyle(style) {
  selectedStyle.value = style
}

async function generate() {
  if (!imageUrl.value || !selectedStyle.value || !imageFile.value) return
  loading.value = true
  result.value = null
  errorMsg.value = ''

  const res = await requestHairstyleGenerate({
    image: imageFile.value,
    style: selectedStyle.value,
    gender: gender.value,
    beautyLevel: beautyLevel.value,
  })

  loading.value = false

  if (!res.ok) {
    errorMsg.value = res.message || '生成失败，请换一张正脸清晰照片再试。'
    return
  }

  result.value = res.data
}

function tryAnotherStyle() {
  result.value = null
  errorMsg.value = ''
}

onUnmounted(() => {
  if (objectUrl) URL.revokeObjectURL(objectUrl)
})
</script>

<template>
  <div class="page">
    <nav class="top-nav">
      <RouterLink class="nav-link" to="/">← 首页</RouterLink>
    </nav>

    <!-- Hero -->
    <header class="hero card">
      <h1 class="title">AI测你适合什么发型</h1>
      <p class="sub">上传或直接拍一张自拍，AI帮你生成不同发型效果，看看哪种更适合你。</p>
    </header>

    <!-- Upload area (no image selected yet) -->
    <section v-if="!imageUrl" class="section card upload-section">
      <label class="upload-label" for="hairstyle-photo">
        <div class="upload-icon">📷</div>
        <div class="upload-text">立即拍照 / 上传照片</div>
        <div class="upload-hint">支持 JPG / PNG，建议正脸清晰照</div>
      </label>
      <!-- capture="user" 优先唤起前置摄像头；部分设备会限制相册，可按需去掉 capture 属性 -->
      <input
        id="hairstyle-photo"
        type="file"
        accept="image/*"
        capture="user"
        class="file-input"
        @change="handleFileChange"
      />
    </section>

    <!-- Configure & result (after image selected) -->
    <template v-if="imageUrl">
      <!-- Original image preview -->
      <section class="section card preview-section">
        <div class="preview-header">
          <span class="section-label">原图预览</span>
          <button class="re-upload-btn" @click="resetUpload">重新上传</button>
        </div>
        <div class="preview-wrap">
          <img :src="imageUrl" alt="原图预览" class="preview-img" />
        </div>
      </section>

      <!-- Style selection -->
      <section class="section card style-section">
        <span class="section-label">选择发型风格</span>

        <div class="gender-toggle">
          <button
            :class="['gender-btn', { active: gender === 'female' }]"
            @click="setGender('female')"
          >
            女生
          </button>
          <button
            :class="['gender-btn', { active: gender === 'male' }]"
            @click="setGender('male')"
          >
            男生
          </button>
        </div>

        <div class="style-grid">
          <button
            v-for="style in gender === 'male' ? MALE_STYLES : FEMALE_STYLES"
            :key="style"
            :class="['style-chip', { selected: selectedStyle === style }]"
            @click="selectStyle(style)"
          >
            {{ style }}
          </button>
        </div>
      </section>

      <!-- Beauty level selection -->
      <section class="section card beauty-section">
        <span class="section-label">效果强度</span>
        <div class="beauty-options">
          <button
            v-for="opt in BEAUTY_OPTIONS"
            :key="opt.value"
            :class="['beauty-option', { selected: beautyLevel === opt.value }]"
            @click="beautyLevel = opt.value"
          >
            <span class="beauty-option-name">{{ opt.name }}</span>
            <span class="beauty-option-desc">{{ opt.desc }}</span>
          </button>
        </div>
      </section>

      <!-- Generate button -->
      <button
        class="btn-gradient generate-btn"
        :disabled="!selectedStyle || loading"
        @click="generate"
      >
        <span v-if="loading" class="btn-loading">
          <span class="loading-dot" />AI 生成中...
        </span>
        <span v-else>开始生成</span>
      </button>

      <!-- Error message -->
      <div v-if="errorMsg" class="error-card">
        <p class="error-text">{{ errorMsg }}</p>
        <button class="error-retry-btn" @click="tryAnotherStyle">重新选择发型</button>
      </div>

      <!-- Result section -->
      <section v-if="loading || result" class="section card result-section">
        <span class="section-label">生成结果</span>

        <!-- Loading state -->
        <div v-if="loading" class="loading-state">
          <div class="spinner" />
          <p class="loading-text">AI正在帮你换发型，大约需要几十秒...</p>
        </div>

        <!-- Result state -->
        <template v-else-if="result">
          <div class="result-compare">
            <div class="result-img-wrap">
              <p class="result-img-label">原图</p>
              <img :src="imageUrl" alt="原图" class="result-img" />
            </div>
            <div class="result-img-wrap">
              <p class="result-img-label">AI 效果图</p>
              <img
                v-if="result.resultImageUrl"
                :src="staticUrl(result.resultImageUrl)"
                alt="AI换发型效果"
                class="result-img"
              />
              <div v-else class="result-placeholder">
                <p class="placeholder-text">这里将展示 AI 生成后的发型效果图</p>
              </div>
            </div>
          </div>

          <div class="suggestion-card">
            <p class="suggestion-label">✨ AI 建议</p>
            <p class="suggestion-text">{{ result.suggestion }}</p>
          </div>

          <button class="try-again-btn" @click="tryAnotherStyle">换个发型试试</button>
        </template>
      </section>
    </template>

    <!-- Tips -->
    <section class="tips-card">
      <p class="tips-title">温馨提示</p>
      <ul class="tips-list">
        <li>建议使用正脸、光线清晰的照片</li>
        <li>刘海、帽子、遮挡脸部会影响生成效果</li>
        <li>AI结果仅供参考，真实剪发前建议咨询发型师</li>
      </ul>
    </section>
  </div>
</template>

<style scoped>
.page {
  max-width: 520px;
  margin: 0 auto;
  padding: 16px 14px 48px;
  min-height: 100vh;
}

.top-nav {
  padding: 0 2px 12px;
}

.nav-link {
  font-size: 14px;
  font-weight: 600;
  color: #6366f1;
  text-decoration: none;
}

.hero {
  margin-bottom: 16px;
}

.card {
  background: var(--surface-solid);
  border-radius: var(--radius);
  padding: 18px 16px;
  border: var(--border-soft);
  box-shadow: var(--shadow-card);
}

.title {
  margin: 0 0 8px;
  font-size: 22px;
  font-weight: 800;
  color: var(--text);
  line-height: 1.35;
}

.sub {
  margin: 0;
  font-size: 14px;
  line-height: 1.65;
  color: var(--text-muted);
}

.section {
  margin-bottom: 12px;
}

.section-label {
  display: block;
  font-size: 13px;
  font-weight: 700;
  color: var(--text-muted);
  margin-bottom: 14px;
  letter-spacing: 0.03em;
}

/* Upload */
.upload-section {
  text-align: center;
  padding: 36px 16px;
  cursor: pointer;
  border: 2px dashed rgba(99, 102, 241, 0.35);
  transition: border-color var(--transition), box-shadow var(--transition);
  margin-bottom: 12px;
}

.upload-section:hover {
  border-color: rgba(99, 102, 241, 0.6);
  box-shadow: var(--shadow-float);
}

.upload-label {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  cursor: pointer;
}

.upload-icon {
  font-size: 40px;
  line-height: 1;
}

.upload-text {
  font-size: 17px;
  font-weight: 700;
  color: var(--text);
}

.upload-hint {
  font-size: 13px;
  color: var(--text-muted);
}

.file-input {
  position: absolute;
  width: 1px;
  height: 1px;
  opacity: 0;
  pointer-events: none;
}

/* Preview */
.preview-section {
  margin-bottom: 12px;
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.preview-header .section-label {
  margin-bottom: 0;
}

.re-upload-btn {
  font-size: 13px;
  font-weight: 600;
  color: #6366f1;
  background: none;
  border: none;
  padding: 4px 0;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 3px;
}

.preview-wrap {
  border-radius: var(--radius-sm);
  overflow: hidden;
  background: rgba(148, 163, 184, 0.1);
  text-align: center;
}

.preview-img {
  width: 100%;
  max-height: 280px;
  object-fit: contain;
  display: block;
}

/* Style selection */
.style-section {
  margin-bottom: 12px;
}

.gender-toggle {
  display: flex;
  gap: 8px;
  margin-bottom: 14px;
}

.gender-btn {
  flex: 1;
  padding: 10px;
  border-radius: var(--radius-sm);
  font-size: 15px;
  font-weight: 600;
  background: rgba(148, 163, 184, 0.1);
  border: 1px solid rgba(148, 163, 184, 0.25);
  color: var(--text-muted);
  transition:
    background var(--transition),
    color var(--transition),
    border-color var(--transition);
}

.gender-btn.active {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.12), rgba(168, 85, 247, 0.1));
  border-color: rgba(99, 102, 241, 0.4);
  color: #4338ca;
}

.style-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

@media (max-width: 360px) {
  .style-grid {
    grid-template-columns: repeat(2, 1fr);
  }
}

.style-chip {
  padding: 10px 4px;
  border-radius: var(--radius-sm);
  font-size: 14px;
  font-weight: 500;
  background: rgba(148, 163, 184, 0.08);
  border: 1px solid rgba(148, 163, 184, 0.22);
  color: var(--text);
  cursor: pointer;
  transition:
    background var(--transition),
    border-color var(--transition),
    color var(--transition),
    transform var(--transition);
}

.style-chip:hover {
  transform: translateY(-1px);
  border-color: rgba(99, 102, 241, 0.35);
}

.style-chip.selected {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.14), rgba(168, 85, 247, 0.12));
  border-color: rgba(99, 102, 241, 0.5);
  color: #4338ca;
  font-weight: 700;
}

/* Generate button */
.generate-btn {
  display: block;
  width: 100%;
  padding: 16px;
  margin-bottom: 12px;
  border-radius: var(--radius);
  font-size: 17px;
  font-weight: 700;
  letter-spacing: 0.02em;
}

.btn-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.loading-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #fff;
  animation: pulse 1s infinite;
}

@keyframes pulse {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.5; transform: scale(0.8); }
}

/* Result */
.result-section {
  margin-bottom: 12px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 24px 0;
}

.spinner {
  width: 36px;
  height: 36px;
  border: 3px solid rgba(99, 102, 241, 0.2);
  border-top-color: #6366f1;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.loading-text {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #6366f1;
  text-align: center;
}

.result-compare {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 14px;
}

.result-img-wrap {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.result-img-label {
  margin: 0;
  font-size: 12px;
  font-weight: 600;
  color: var(--text-muted);
  text-align: center;
}

.result-img {
  width: 100%;
  border-radius: var(--radius-sm);
  object-fit: cover;
  aspect-ratio: 3 / 4;
}

.result-placeholder {
  width: 100%;
  aspect-ratio: 3 / 4;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.06), rgba(168, 85, 247, 0.06));
  border: 1px dashed rgba(99, 102, 241, 0.3);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 12px;
}

.placeholder-text {
  margin: 0;
  font-size: 12px;
  color: var(--text-muted);
  text-align: center;
  line-height: 1.6;
}

.suggestion-card {
  padding: 14px;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.06), rgba(168, 85, 247, 0.04));
  border: 1px solid rgba(99, 102, 241, 0.15);
  margin-bottom: 14px;
}

.suggestion-label {
  margin: 0 0 6px;
  font-size: 13px;
  font-weight: 700;
  color: #4338ca;
}

.suggestion-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.65;
  color: var(--text);
}

.try-again-btn {
  display: block;
  width: 100%;
  padding: 12px;
  border-radius: var(--radius-sm);
  font-size: 15px;
  font-weight: 600;
  color: #6366f1;
  background: rgba(99, 102, 241, 0.08);
  border: 1px solid rgba(99, 102, 241, 0.2);
  cursor: pointer;
  transition:
    background var(--transition),
    transform var(--transition);
}

.try-again-btn:hover {
  background: rgba(99, 102, 241, 0.14);
  transform: translateY(-1px);
}

/* Error */
.error-card {
  margin-bottom: 12px;
  padding: 14px 16px;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, rgba(254, 226, 226, 0.7), rgba(254, 202, 202, 0.5));
  border: 1px solid rgba(239, 68, 68, 0.3);
}

.error-text {
  margin: 0 0 10px;
  font-size: 14px;
  line-height: 1.6;
  color: #991b1b;
}

.error-retry-btn {
  font-size: 13px;
  font-weight: 600;
  color: #dc2626;
  background: none;
  border: none;
  padding: 0;
  cursor: pointer;
  text-decoration: underline;
  text-underline-offset: 3px;
}

/* Beauty level */
.beauty-section {
  margin-bottom: 12px;
}

.beauty-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.beauty-option {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 3px;
  width: 100%;
  padding: 12px 14px;
  border-radius: var(--radius-sm);
  background: rgba(148, 163, 184, 0.08);
  border: 1px solid rgba(148, 163, 184, 0.22);
  text-align: left;
  cursor: pointer;
  transition:
    background var(--transition),
    border-color var(--transition);
}

.beauty-option:hover {
  border-color: rgba(99, 102, 241, 0.3);
}

.beauty-option.selected {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(168, 85, 247, 0.08));
  border-color: rgba(99, 102, 241, 0.45);
}

.beauty-option-name {
  font-size: 14px;
  font-weight: 700;
  color: var(--text);
  line-height: 1.3;
}

.beauty-option.selected .beauty-option-name {
  color: #4338ca;
}

.beauty-option-desc {
  font-size: 12px;
  color: var(--text-muted);
  line-height: 1.5;
}

/* Tips */
.tips-card {
  padding: 14px 16px;
  border-radius: var(--radius-sm);
  background: linear-gradient(135deg, rgba(254, 243, 199, 0.65), rgba(255, 237, 213, 0.5));
  color: #92400e;
  border: 1px solid rgba(251, 191, 36, 0.35);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.5);
  margin-top: 4px;
}

.tips-title {
  margin: 0 0 8px;
  font-size: 13px;
  font-weight: 700;
}

.tips-list {
  margin: 0;
  padding-left: 18px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.tips-list li {
  font-size: 12px;
  line-height: 1.65;
}
</style>
