/// <reference types="vite/client" />

interface ImportMetaEnv {
  /** Backend API manzili, masalan https://api.moliyadaftari.uz/api/v1 (lokal: /api/v1 — Vite proxy) */
  readonly VITE_API_BASE_URL?: string
  /** Faqat lokal ishlab chiqish: Telegram'siz ochganda qaysi foydalanuvchi bo'lib kirish */
  readonly VITE_DEV_USER_ID?: string
  /** Bot nomi (@ belgisisiz) — to'lov saytidagi Telegram Login uchun */
  readonly VITE_BOT_USERNAME?: string
  /** To'lov sayti manzili (mini app'dagi "Obunani uzaytirish" tugmasi shu yerga ochadi) */
  readonly VITE_SITE_URL?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

declare module "*.vue" {
  import type { DefineComponent } from "vue"
  const component: DefineComponent<object, object, unknown>
  export default component
}
