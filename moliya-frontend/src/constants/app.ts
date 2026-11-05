// Ilova bo'yicha doimiy qiymatlar va muhit o'zgaruvchilari. import.meta.env faqat shu faylda o'qiladi.

export const ENV = {
  /** Backend API. Lokal: /api/v1 (Vite proxy), production: https://moliya-api.onrender.com/api/v1 */
  apiBaseUrl: import.meta.env.VITE_API_BASE_URL || "/api/v1",
  /** Faqat lokal: Telegram'siz brauzerda ochish uchun foydalanuvchi id'si. */
  devUserId: import.meta.env.DEV ? import.meta.env.VITE_DEV_USER_ID : undefined,
  botUsername: import.meta.env.VITE_BOT_USERNAME || "",
  /** To'lov sayti. Bo'sh bo'lsa joriy domen. */
  siteUrl: (import.meta.env.VITE_SITE_URL || window.location.origin).replace(/\/$/, ""),
}

export const DEFAULT_USD_RATE = 12_000

/** Bepul serverda backend uxlab qoladi: birinchi so'rov 50+ soniya ketishi mumkin. */
export const REQUEST_TIMEOUT_MS = 70_000
/** Shundan uzoq yuklansa "server uyg'onmoqda" xabari chiqadi. */
export const SLOW_LOADING_MS = 4_000

export const STORAGE_KEYS = {
  lang: "moliya_lang",
  telegramLogin: "moliya_tg_login",
} as const

/** Telegram mavzusi bilan bir xil fon rangi (styles/tokens.css --bg). */
export const THEME_BG = "#0B1325"
