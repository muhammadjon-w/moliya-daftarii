// Yozish amallari. Har biri keshni darhol (optimistik) yangilaydi, xato bo'lsa orqaga qaytaradi,
// muvaffaqiyatda esa server javobini keshga yozadi — butun holatni qayta yuklash shart emas.
import { useMutation, useQueryClient, type QueryClient } from "@tanstack/vue-query"
import type { DebtDraft, DebtPayment, LedgerSettings, LedgerState, PlanValues, TransactionDraft } from "@/domain/types"
import { useGateways } from "../container"
import { queryKeys } from "../queryKeys"

type Patch = (s: LedgerState) => LedgerState

function optimistic(qc: QueryClient) {
  return {
    async apply(patch: Patch) {
      await qc.cancelQueries({ queryKey: queryKeys.ledger })
      const previous = qc.getQueryData<LedgerState>(queryKeys.ledger)
      if (previous) qc.setQueryData<LedgerState>(queryKeys.ledger, patch(previous))
      return { previous }
    },
    rollback(ctx: { previous?: LedgerState } | undefined) {
      if (ctx?.previous) qc.setQueryData(queryKeys.ledger, ctx.previous)
    },
    set(patch: Patch) {
      const cur = qc.getQueryData<LedgerState>(queryKeys.ledger)
      if (cur) qc.setQueryData<LedgerState>(queryKeys.ledger, patch(cur))
    },
  }
}

const tempId = () => "tmp-" + Math.random().toString(36).slice(2)
const upsert = <T extends { id: string }>(list: T[], item: T, replaceId = item.id) =>
  list.some((x) => x.id === replaceId) ? list.map((x) => (x.id === replaceId ? item : x)) : [...list, item]

export function useSaveTransaction() {
  const { ledger } = useGateways()
  const qc = useQueryClient()
  const o = optimistic(qc)
  return useMutation({
    mutationFn: (v: { id?: string; draft: TransactionDraft; tmp: string }) =>
      v.id ? ledger.updateTransaction(v.id, v.draft) : ledger.createTransaction(v.draft),
    onMutate: (v) => o.apply((s) => ({ ...s, transactions: upsert(s.transactions, { ...v.draft, id: v.id ?? v.tmp, createdAt: null }) })),
    onError: (_e, _v, ctx) => o.rollback(ctx),
    onSuccess: (tx, v) => o.set((s) => ({ ...s, transactions: upsert(s.transactions, tx, v.id ?? v.tmp) })),
  })
}

export function saveTransactionVars(draft: TransactionDraft, id?: string) {
  return { id, draft, tmp: tempId() }
}

export function useDeleteTransaction() {
  const { ledger } = useGateways()
  const o = optimistic(useQueryClient())
  return useMutation({
    mutationFn: (id: string) => ledger.deleteTransaction(id),
    onMutate: (id) => o.apply((s) => ({ ...s, transactions: s.transactions.filter((x) => x.id !== id) })),
    onError: (_e, _v, ctx) => o.rollback(ctx),
  })
}

export function useSaveDebt() {
  const { ledger } = useGateways()
  const o = optimistic(useQueryClient())
  return useMutation({
    mutationFn: (v: { id?: string; draft: DebtDraft; tmp: string }) => (v.id ? ledger.updateDebt(v.id, v.draft) : ledger.createDebt(v.draft)),
    onMutate: (v) => o.apply((s) => ({ ...s, debts: upsert(s.debts, { ...v.draft, id: v.id ?? v.tmp, createdAt: null }) })),
    onError: (_e, _v, ctx) => o.rollback(ctx),
    onSuccess: (debt, v) => o.set((s) => ({ ...s, debts: upsert(s.debts, debt, v.id ?? v.tmp) })),
  })
}

export function saveDebtVars(draft: DebtDraft, id?: string) {
  return { id, draft, tmp: tempId() }
}

export function useDeleteDebt() {
  const { ledger } = useGateways()
  const o = optimistic(useQueryClient())
  return useMutation({
    mutationFn: (id: string) => ledger.deleteDebt(id),
    onMutate: (id) => o.apply((s) => ({ ...s, debts: s.debts.filter((x) => x.id !== id) })),
    onError: (_e, _v, ctx) => o.rollback(ctx),
  })
}

export function usePayDebt() {
  const { ledger } = useGateways()
  const o = optimistic(useQueryClient())
  return useMutation({
    mutationFn: (v: { id: string; payment: DebtPayment }) => ledger.payDebt(v.id, v.payment),
    onSuccess: ({ debt, transaction }) =>
      o.set((s) => ({ ...s, debts: upsert(s.debts, debt), transactions: transaction ? upsert(s.transactions, transaction) : s.transactions })),
  })
}

export function useSavePlan() {
  const { ledger } = useGateways()
  const o = optimistic(useQueryClient())
  return useMutation({
    mutationFn: (v: { month: string; values: PlanValues }) => ledger.savePlan(v.month, v.values),
    onMutate: (v) => o.apply((s) => ({ ...s, plans: { ...s.plans, [v.month]: v.values } })),
    onError: (_e, _v, ctx) => o.rollback(ctx),
    onSuccess: (values, v) => o.set((s) => ({ ...s, plans: { ...s.plans, [v.month]: values } })),
  })
}

export function useCopyPreviousPlan() {
  const { ledger } = useGateways()
  const o = optimistic(useQueryClient())
  return useMutation({
    mutationFn: (month: string) => ledger.copyPreviousPlan(month),
    onSuccess: (values, month) => o.set((s) => ({ ...s, plans: { ...s.plans, [month]: values } })),
  })
}

export function useUpdateSettings() {
  const { ledger } = useGateways()
  const o = optimistic(useQueryClient())
  return useMutation({
    mutationFn: (patch: Partial<LedgerSettings>) => ledger.updateSettings(patch),
    onMutate: (patch) => o.apply((s) => ({ ...s, settings: { ...s.settings, ...patch } })),
    onError: (_e, _v, ctx) => o.rollback(ctx),
    onSuccess: (settings) => o.set((s) => ({ ...s, settings })),
  })
}

export function useExportExcel() {
  const { ledger } = useGateways()
  return useMutation({ mutationFn: (month: string) => ledger.exportExcel(month) })
}
