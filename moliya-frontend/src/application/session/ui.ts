// Interfeys holati (server ma'lumoti emas): tanlangan oy, til, bildirishnoma, obuna oynasi.
import { defineStore } from "pinia"
import { ref } from "vue"
import { shiftMonth } from "@/domain/money"
import type { Period } from "@/domain/types"

export type Lang = "uz" | "ru" | "en"
const LANG_KEY = "moliya_lang"

function readLang(fallback: string | null): Lang {
  let v: string | null = null
  try {
    v = localStorage.getItem(LANG_KEY)
  } catch {
    /* brauzer xotirasi yopiq bo'lishi mumkin */
  }
  const c = v || fallback || "uz"
  return c === "ru" || c === "en" ? c : "uz"
}

export const useUiStore = defineStore("ui", () => {
  const now = new Date()
  const period = ref<Period>({ y: now.getFullYear(), m: now.getMonth() })
  const lang = ref<Lang>("uz")
  const toast = ref<{ text: string; error: boolean; id: number } | null>(null)
  const paywallOpen = ref(false)

  function initLang(telegramLang: string | null) {
    lang.value = readLang(telegramLang)
  }
  function setLang(l: Lang) {
    lang.value = l
    try {
      localStorage.setItem(LANG_KEY, l)
    } catch {
      /* e'tiborsiz */
    }
  }
  function setPeriod(p: Period) {
    period.value = { ...p }
  }
  function shift(delta: number, unit: "month" | "year" = "month") {
    period.value = unit === "year" ? { y: period.value.y + delta, m: period.value.m } : shiftMonth(period.value.y, period.value.m, delta)
  }
  let timer: ReturnType<typeof setTimeout> | undefined
  function notify(text: string, error = false) {
    toast.value = { text, error, id: Date.now() }
    clearTimeout(timer)
    timer = setTimeout(() => (toast.value = null), error ? 6000 : 2200)
  }

  return { period, lang, toast, paywallOpen, initLang, setLang, setPeriod, shift, notify }
})
