// Ledger holatini o'qish: bitta so'rov (GET ledger/state), qolgani shu keshdan hisoblanadi.
import { useQuery } from "@tanstack/vue-query"
import { computed } from "vue"
import { DEFAULT_USD_RATE } from "@/domain/ledger"
import type { LedgerState } from "@/domain/types"
import { useGateways } from "../container"
import { queryKeys } from "../queryKeys"

export const EMPTY_STATE: LedgerState = {
  access: { state: "trial", trialEndsAt: new Date().toISOString(), paidUntil: null, daysLeft: 30, canWrite: true },
  transactions: [],
  debts: [],
  plans: {},
  settings: { usdRate: DEFAULT_USD_RATE, openingBalance: 0 },
}

export function useLedgerState() {
  const { ledger } = useGateways()
  const query = useQuery({
    queryKey: queryKeys.ledger,
    queryFn: () => ledger.state(),
    staleTime: 30_000,
  })
  const state = computed<LedgerState>(() => query.data.value ?? EMPTY_STATE)
  const usdRate = computed(() => (state.value.settings.usdRate > 0 ? state.value.settings.usdRate : DEFAULT_USD_RATE))
  return { query, state, usdRate }
}
