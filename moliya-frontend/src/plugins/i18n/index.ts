// Tarjima: lug'atlar va til tanlash. Komponentlar buni composables/useI18n orqali ishlatadi.
import { STORAGE_KEYS } from "@/constants/app"
import type { Lang } from "@/types/ui"
import { en } from "./en"
import { ru } from "./ru"
import { uz, type MessageKey, type Messages } from "./uz"

export type { MessageKey }

const DICTS: Record<Lang, Messages> = { uz, ru, en }
export const LANGS: readonly Lang[] = ["uz", "ru", "en"]

/** {name} o'rniga qiymat qo'yadi. */
export function translate(lang: Lang, key: MessageKey, vars?: Record<string, string | number>): string {
  const v = DICTS[lang][key]
  let s = typeof v === "string" ? v : key
  if (vars) for (const [k, val] of Object.entries(vars)) s = s.replace("{" + k + "}", String(val))
  return s
}

export function messageList(lang: Lang, key: MessageKey): string[] {
  const v = DICTS[lang][key]
  return Array.isArray(v) ? v : []
}

/** Saqlangan til → Telegram tili → o'zbekcha. */
export function detectLang(telegramLang: string | null): Lang {
  let saved: string | null = null
  try {
    saved = localStorage.getItem(STORAGE_KEYS.lang)
  } catch {
    /* brauzer xotirasi yopiq bo'lishi mumkin */
  }
  const c = saved || telegramLang || "uz"
  return (LANGS as readonly string[]).includes(c) ? (c as Lang) : "uz"
}

export function rememberLang(lang: Lang) {
  try {
    localStorage.setItem(STORAGE_KEYS.lang, lang)
  } catch {
    /* e'tiborsiz */
  }
}
