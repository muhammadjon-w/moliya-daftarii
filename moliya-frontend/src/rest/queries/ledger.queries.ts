// Hisob holatini o'qish: bitta so'rov (GET ledger/state), qolgan hamma narsa shu keshdan hisoblanadi.
import { useQuery } from "@tanstack/vue-query"
import { computed } from "vue"
import { DEFAULT_USD_RATE } from "@/constants/app"
import { queryKeys } from "@/constants/queryKeys"
import type { LedgerState } from "@/types/api"
import { ledgerService } from "../services/ledger.service"

export const EMPTY_STATE: LedgerState = {
  account: null,
  access: { state: "trial", trialEndsAt: new Date().toISOString(), paidUntil: null, daysLeft: 30, canWrite: true },
  transactions: [],
  debts: [],
  plans: {},
  settings: { usdRate: DEFAULT_USD_RATE, openingBalance: 0 },
}

export function useLedgerQuery() {
  const query = useQuery({
    queryKey: queryKeys.ledger,
    queryFn: ledgerService.state,
    staleTime: 30_000,
  })
  const state = computed<LedgerState>(() => query.data.value ?? EMPTY_STATE)
  const usdRate = computed(() => (state.value.settings.usdRate > 0 ? state.value.settings.usdRate : DEFAULT_USD_RATE))
  return { query, state, usdRate }
}
