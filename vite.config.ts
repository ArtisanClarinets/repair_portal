import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
  plugins: [vue()],
  build: {
    ssr: 'classic',
    outDir: 'public/dist',
    emptyOutDir: false,
  },
});
