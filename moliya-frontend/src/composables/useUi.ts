// Interfeys holati (server ma'lumoti emas): tanlangan oy, til, bildirishnoma, ochiq oyna.
// Bitta umumiy reaktiv obyekt — Pinia shart emas. Server ma'lumoti bu yerda SAQLANMAYDI (u TanStack Query keshida).
import { reactive, readonly } from "vue"
import { detectLang, rememberLang } from "@/plugins/i18n"
import { telegram } from "@/plugins/telegram"
import type { Period } from "@/types/ledger"
import type { Lang, Sheet, Toast } from "@/types/ui"
import { shiftMonth } from "@/utils/money"

const now = new Date()
const state = reactive({
  period: { y: now.getFullYear(), m: now.getMonth() } as Period,
  lang: detectLang(telegram.languageCode) as Lang,
  toast: null as Toast | null,
  sheet: null as Sheet | null,
  paywallOpen: false,
})

let toastTimer: ReturnType<typeof setTimeout> | undefined

const actions = {
  setLang(lang: Lang) {
    state.lang = lang
    rememberLang(lang)
    document.documentElement.lang = lang
  },
  setPeriod(p: Period) {
    state.period = { ...p }
  },
  shiftPeriod(delta: number) {
    state.period = shiftMonth(state.period.y, state.period.m, delta)
  },
  notify(text: string, error = false) {
    state.toast = { id: Date.now(), text, error }
    clearTimeout(toastTimer)
    toastTimer = setTimeout(() => (state.toast = null), error ? 6000 : 2400)
  },
  /** Oynani ochish uchun odatda composables/useSheets dan foydalaning (u obunani ham tekshiradi). */
  openSheet(sheet: Sheet) {
    state.sheet = sheet
  },
  closeSheet() {
    state.sheet = null
  },
  openPaywall() {
    state.sheet = null
    state.paywallOpen = true
  },
  closePaywall() {
    state.paywallOpen = false
  },
}

export function useUi() {
  return { ui: readonly(state), ...actions }
}
