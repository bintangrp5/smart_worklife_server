import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  base: '/admin_assets/',
  build: {
    outDir: '../admin_dist',
    emptyOutDir: true,
  }
})
