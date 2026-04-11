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
    },
  },
})
