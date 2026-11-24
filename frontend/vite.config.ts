/// <reference types="vitest" />
import { defineConfig, loadEnv } from 'vite';
import react from '@vitejs/plugin-react';

// O frontend roda na porta 3000, já liberada no CORS do backend
// (BACKEND_CORS_ORIGINS em backend/app/core/config.py).
// Em desenvolvimento, as rotas /health e /api são encaminhadas ao backend
// via proxy, evitando dependência de CORS e de URLs fixas.
export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '');
  const target = env.VITE_PROXY_TARGET || 'http://localhost:8000';
  const proxy = {
    '/health': { target, changeOrigin: true },
    '/api': { target, changeOrigin: true },
  };

  return {
    plugins: [react()],
    server: { port: 3000, strictPort: true, proxy },
    preview: { port: 3000, strictPort: true, proxy },
    test: {
      environment: 'jsdom',
      setupFiles: './src/test/setup.ts',
      css: false,
    },
  };
});
