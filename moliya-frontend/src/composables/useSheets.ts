// Pastki oynalarni ochish. Yozish oynalari obuna tugagan bo'lsa to'lov oynasini ochadi.
import { useLedgerQuery } from "@/rest/queries/ledger.queries"
import type { Debt, Transaction, TxType } from "@/types/ledger"
import { useTelegram } from "./useTelegram"
import { useUi } from "./useUi"

export function useSheets() {
  const { state } = useLedgerQuery()
  const { openSheet, openPaywall } = useUi()
  const tg = useTelegram()

  /** Faqat ko'rish uchun ochiladigan oynalar (tahrirlash) obunasiz ham ochiladi — server o'zi 402 qaytaradi. */
  function guarded(open: () => void) {
    tg.haptic("light")
    if (state.value.access.canWrite) open()
    else openPaywall()
  }

  return {
    newRecord: (type: TxType) => guarded(() => openSheet({ kind: "record", type })),
    editRecord: (tx: Transaction) => openSheet({ kind: "record", type: tx.type, tx }),
    newDebt: () => guarded(() => openSheet({ kind: "debt" })),
    editDebt: (debt: Debt) => openSheet({ kind: "debt", debt }),
    payDebt: (debt: Debt) => guarded(() => openSheet({ kind: "pay", debt })),
    settings: () => openSheet({ kind: "settings" }),
    monthPicker: () => openSheet({ kind: "month" }),
    paywall: openPaywall,
  }
}
