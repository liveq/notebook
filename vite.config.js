import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/notebook/',  // GitHub Pages 경로
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
  },
})
