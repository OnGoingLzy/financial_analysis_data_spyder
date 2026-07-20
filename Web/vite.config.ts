import { fileURLToPath, URL } from 'node:url'
import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vitest/config'

export default defineConfig({
  plugins: [vue()],
  resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
  server: { proxy: { '/api': 'http://127.0.0.1:5174' } },
  build: { chunkSizeWarningLimit: 600, rollupOptions: { output: { manualChunks: { charts: ['echarts'], framework: ['vue', 'vue-router', 'pinia'] } } } },
  test: { environment: 'jsdom' },
})
