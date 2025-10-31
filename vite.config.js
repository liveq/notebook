import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: './',  // 상대 경로 사용 (어디서든 작동)
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
})
