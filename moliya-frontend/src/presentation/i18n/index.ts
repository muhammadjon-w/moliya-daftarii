// Tarjima va yorliqlar: joriy til Pinia store'da, matnlar messages.ts + extra.ts da.
import { storeToRefs } from "pinia"
import { CATEGORIES, ITEM_BY_ID } from "@/domain/catalog"
import { compact } from "@/domain/money"
import type { Group, Method } from "@/domain/types"
import { useUiStore, type Lang } from "@/application/session/ui"
import { extra } from "./extra"
import { messages } from "./messages"

const IDX: Record<Lang, 0 | 1 | 2> = { uz: 0, ru: 1, en: 2 }

type Dict = Record<string, string | readonly string[]>
const dict = (l: Lang): Dict => ({ ...(messages[l] as Dict), ...(extra[l] as Dict) })
const DICTS: Record<Lang, Dict> = { uz: dict("uz"), ru: dict("ru"), en: dict("en") }

export function translate(lang: Lang, key: string, vars?: Record<string, string | number>): string {
  const v = DICTS[lang][key] ?? DICTS.uz[key]
  let s = typeof v === "string" ? v : key
  if (vars) for (const [k, val] of Object.entries(vars)) s = s.replace("{" + k + "}", String(val))
  return s
}

export function useI18n() {
  const { lang } = storeToRefs(useUiStore())

  const t = (key: string, vars?: Record<string, string | number>) => translate(lang.value, key, vars)
  const list = (key: string): string[] => {
    const v = DICTS[lang.value][key] ?? DICTS.uz[key]
    return Array.isArray(v) ? [...v] : []
  }
  const months = () => list("months")
  const monthName = (m: number) => months()[m] ?? ""
  const itemLabel = (id: string) => ITEM_BY_ID[id]?.labels[IDX[lang.value]] ?? (id || "—")
  const catLabel = (id: string) => CATEGORIES[id]?.[IDX[lang.value]] ?? (id || "—")
  const methodLabel = (m: Method | string) => t("m_" + m)
  const groupLabel = (g: Group) => t("g_" + g)
  const sum = (n: number) => numWithSum(n)
  const numWithSum = (n: number) => Math.round(n).toLocaleString("ru-RU").replace(/\s/g, " ") + " " + t("sum")
  const signedSum = (n: number) => (n < 0 ? "−" : "") + numWithSum(Math.abs(n))
  const kcompact = (n: number) =>
    compact(n, lang.value === "ru" ? { billion: "млрд", million: "млн", decimal: "," } : lang.value === "en" ? { billion: "B", million: "M", decimal: "." } : { billion: "mlrd", million: "mln", decimal: "," })

  function todayText(d = new Date()) {
    if (lang.value === "uz") return `${list("weekdays")[d.getDay()]}, ${d.getDate()}-${monthName(d.getMonth()).toLowerCase()} ${d.getFullYear()}`
    const s = new Intl.DateTimeFormat(lang.value === "ru" ? "ru-RU" : "en-GB", { weekday: "long", day: "numeric", month: "long", year: "numeric" }).format(d)
    return s.charAt(0).toUpperCase() + s.slice(1)
  }
  function greeting(name: string | null, d = new Date()) {
    const h = d.getHours()
    const k = h >= 5 && h < 12 ? "greet_morning" : h >= 12 && h < 18 ? "greet_day" : "greet_evening"
    return t(k) + (name ? ", " + name : "")
  }

  return { lang, t, months, monthName, itemLabel, catLabel, methodLabel, groupLabel, sum, signedSum, kcompact, todayText, greeting }
}
