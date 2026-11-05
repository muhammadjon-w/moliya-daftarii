// Tanlangan oy uchun hisoblangan ko'rsatkichlar. Komponentlar shu yerdan oladi, o'zlari hisoblamaydi.
import { storeToRefs } from "pinia"
import { computed } from "vue"
import { balanceBefore, monthTransactions, totals } from "@/domain/ledger"
import { monthKey, todayIso } from "@/domain/money"
import { useUiStore } from "../session/ui"
import { useLedgerState } from "./queries"

export function useMonth() {
  const { state, usdRate, query } = useLedgerState()
  const { period } = storeToRefs(useUiStore())

  const key = computed(() => monthKey(period.value.y, period.value.m))
  const list = computed(() => monthTransactions(state.value.transactions, period.value.y, period.value.m))
  const sums = computed(() => totals(list.value, usdRate.value))
  const opening = computed(() => Number(state.value.settings.openingBalance) || 0)
  const startBalance = computed(() => balanceBefore(state.value.transactions, period.value.y, period.value.m, usdRate.value, opening.value))
  const plan = computed(() => state.value.plans[key.value] ?? {})
  const today = todayIso()

  return { state, usdRate, query, period, key, list, sums, opening, startBalance, plan, today }
}
