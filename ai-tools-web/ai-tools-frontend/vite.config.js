import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 5173,
    proxy: {
      // 与线上一致：/api/* → 后端真实路径（与 nginx location /api/ 行为对齐）
      '/api/summary': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: () => '/summary',
      },
      '/api/medical-assistant': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: () => '/prepare-consult',
      },
      '/api/health': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: () => '/health',
      },
      '/api/model-compare': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: () => '/model-compare',
      },
      '/api/offer-decision': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: () => '/offer-decision',
      },
      '/api/evening-plan': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: () => '/evening-plan',
      },
      '/api/interest-explorer': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: () => '/interest-explorer',
      },
      '/api/life-rpg/create-route': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: () => '/life-rpg/create-route',
      },
      '/api/life-rpg/daily': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: () => '/life-rpg/daily',
      },
      '/api/ai-short-drama': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/generated': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/uploads': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
      '/api/memory/compare': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: () => '/memory/compare',
      },
      '/api/tools/xiaohongshu-agent/generate-stream': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: () => '/tools/xiaohongshu-agent/generate-stream',
      },
      '/api/tools/xiaohongshu-agent/generate': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: () => '/tools/xiaohongshu-agent/generate',
      },
      '/api/track': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/api/rag': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
