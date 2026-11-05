import { fileURLToPath, URL } from "node:url"
import vue from "@vitejs/plugin-vue"
import { defineConfig } from "vitest/config"

export default defineConfig({
  plugins: [vue()],
  resolve: { alias: { "@": fileURLToPath(new URL("./src", import.meta.url)) } },
  server: {
    port: 5173,
    // Lokal: /api so'rovlari Django'ga (CORS kerak bo'lmaydi)
    proxy: { "/api": { target: "http://localhost:8000", changeOrigin: true } },
  },
  test: { environment: "jsdom", include: ["tests/**/*.spec.ts"] },
})
