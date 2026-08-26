import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'
import { VitePWA } from 'vite-plugin-pwa'

export default defineConfig({
  // GitHub Actions 部署到 Pages 时使用仓库子路径
  base: process.env.GITHUB_ACTIONS ? '/xiangqicanju/' : '/',
  plugins: [
    react(),
    VitePWA({
      registerType: 'autoUpdate',
      includeAssets: ['favicon.svg'],
      manifest: {
        name: '例胜残局',
        short_name: '例胜残局',
        description: '象棋例胜残局练习，一点开局，本地 AI 防守',
        theme_color: '#1a1510',
        background_color: '#1a1510',
        display: 'standalone',
        orientation: 'portrait',
        lang: 'zh-CN',
        start_url: '.',
        scope: '.',
        icons: [
          {
            src: 'favicon.svg',
            sizes: 'any',
            type: 'image/svg+xml',
            purpose: 'any maskable',
          },
        ],
      },
      workbox: {
        globPatterns: ['**/*.{js,css,html,svg,json,ico,woff2,wasm,data}'],
        maximumFileSizeToCacheInBytes: 6 * 1024 * 1024,
        navigateFallback: 'index.html',
      },
    }),
  ],
  worker: {
    format: 'es',
  },
  server: {
    host: true,
    headers: {
      // 部分 WASM 场景需要；单线程皮卡鱼一般可不依赖
      'Cross-Origin-Opener-Policy': 'same-origin',
      'Cross-Origin-Embedder-Policy': 'require-corp',
    },
  },
})
