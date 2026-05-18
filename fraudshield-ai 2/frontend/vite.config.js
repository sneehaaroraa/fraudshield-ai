import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  // Proxy /api → FastAPI backend during local development
  // In production, VITE_API_BASE_URL points to the deployed backend
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },

  build: {
    outDir: 'dist',
    sourcemap: false,
  },
});
