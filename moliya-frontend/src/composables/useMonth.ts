// Tanlangan oy ko'rsatkichlari: yozuvlar, yig'indilar, qoldiq, reja. Hammasi ledger keshidan hisoblanadi.
import { computed } from "vue"
import { useLedgerQuery } from "@/rest/queries/ledger.queries"
import { balanceBefore, monthTransactions, sortNewestFirst, totals } from "@/utils/ledger"
import { monthKey, shiftMonth, todayIso } from "@/utils/money"
import { useUi } from "./useUi"

export function useMonth() {
  const { query, state, usdRate } = useLedgerQuery()
  const { ui } = useUi()

  const period = computed(() => ui.period)
  const key = computed(() => monthKey(period.value.y, period.value.m))
  const list = computed(() => sortNewestFirst(monthTransactions(state.value.transactions, period.value.y, period.value.m)))
  const sums = computed(() => totals(list.value, usdRate.value))

  const prevPeriod = computed(() => shiftMonth(period.value.y, period.value.m, -1))
  const prevSums = computed(() => totals(monthTransactions(state.value.transactions, prevPeriod.value.y, prevPeriod.value.m), usdRate.value))

  const startBalance = computed(() => balanceBefore(state.value.transactions, period.value.y, period.value.m, usdRate.value, state.value.settings.openingBalance))
  const endBalance = computed(() => startBalance.value + sums.value.net)

  const plan = computed(() => state.value.plans[key.value] ?? {})
  const today = todayIso()

  return { query, state, usdRate, period, key, list, sums, prevSums, startBalance, endBalance, plan, today }
}
