// Tarjima va formatlash: matnlar, pul, sana, katalog yorliqlari — joriy tilda.
import { CATEGORIES, ITEM_BY_ID } from "@/constants/catalog"
import { messageList, translate, type MessageKey } from "@/plugins/i18n"
import type { Currency, Group, Method } from "@/types/ledger"
import type { Lang } from "@/types/ui"
import { compact as compactNum, num } from "@/utils/money"
import { useUi } from "./useUi"

const LABEL_IDX: Record<Lang, 0 | 1 | 2> = { uz: 0, ru: 1, en: 2 }

export function useI18n() {
  const { ui } = useUi()

  const t = (key: MessageKey, vars?: Record<string, string | number>) => translate(ui.lang, key, vars)
  const monthName = (m: number) => messageList(ui.lang, "months")[m] ?? ""
  const periodLabel = (p: { y: number; m: number }) => `${monthName(p.m)} ${p.y}`

  /** Katalogdagi modda nomi; katalogda yo'q bo'lsa foydalanuvchi yozgan matn. */
  const itemLabel = (id: string) => ITEM_BY_ID[id]?.labels[LABEL_IDX[ui.lang]] ?? (id || "—")
  const catLabel = (id: string) => CATEGORIES[id]?.[LABEL_IDX[ui.lang]] ?? (id || "—")
  /** "Yangi yozuv" plitkasidagi qisqa nom (tile_<id>), bo'lmasa modda nomi. */
  const tileLabel = (id: string) => {
    const key = ("tile_" + id) as MessageKey
    const s = translate(ui.lang, key)
    return s === key ? itemLabel(id) : s
  }
  const methodLabel = (m: Method) => t(("m_" + m) as MessageKey)
  const groupLabel = (g: Group) => t(("g_" + g) as MessageKey)

  /** 2 600 000 */
  const money = (n: number) => num(n)
  /** 2 600 000 so'm */
  const sum = (n: number) => num(n) + " " + t("sum")
  /** +14 000 000 / −2 600 000 (dollar bo'lsa "$ 100") */
  const signedAmount = (n: number, positive: boolean, currency: Currency = "UZS") =>
    (positive ? "+" : "−") + (currency === "USD" ? "$ " : "") + num(Math.abs(n))
  /** 28,4 mln */
  const compact = (n: number) => compactNum(n, { billion: t("billion"), million: t("million"), decimal: t("decimal") })

  function greeting(d = new Date()) {
    const h = d.getHours()
    return t(h >= 5 && h < 12 ? "greet_morning" : h >= 12 && h < 18 ? "greet_day" : "greet_evening")
  }

  return { t, monthName, periodLabel, itemLabel, catLabel, tileLabel, methodLabel, groupLabel, money, sum, signedAmount, compact, greeting }
}
