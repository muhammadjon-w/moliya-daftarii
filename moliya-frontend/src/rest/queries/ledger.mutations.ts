// Yozish amallari. Har biri keshni darhol (optimistik) yangilaydi, xato bo'lsa orqaga qaytaradi,
// muvaffaqiyatda esa server javobini keshga yozadi — butun holatni qayta yuklash shart emas.
// Xatolar (402 → to'lov oynasi, boshqalari → bildirishnoma) plugins/vueQuery.ts da bir joyda ushlanadi.
import { useMutation, useQueryClient, type QueryClient } from "@tanstack/vue-query"
import { queryKeys } from "@/constants/queryKeys"
import type { LedgerState } from "@/types/api"
import type { DebtDraft, DebtPayment, LedgerSettings, PlanValues, TransactionDraft } from "@/types/ledger"
import { ledgerService } from "../services/ledger.service"

type Patch = (s: LedgerState) => LedgerState
type Ctx = { previous?: LedgerState }

function cache(qc: QueryClient) {
  return {
    async optimistic(patch: Patch): Promise<Ctx> {
      await qc.cancelQueries({ queryKey: queryKeys.ledger })
      const previous = qc.getQueryData<LedgerState>(queryKeys.ledger)
      if (previous) qc.setQueryData<LedgerState>(queryKeys.ledger, patch(previous))
      return { previous }
    },
    rollback(ctx: Ctx | undefined) {
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
  const c = cache(useQueryClient())
  return useMutation({
    mutationFn: (v: { id?: string; draft: TransactionDraft; tmp: string }) =>
      v.id ? ledgerService.updateTransaction(v.id, v.draft) : ledgerService.createTransaction(v.draft),
    onMutate: (v) => c.optimistic((s) => ({ ...s, transactions: upsert(s.transactions, { ...v.draft, id: v.id ?? v.tmp, createdAt: new Date().toISOString() }) })),
    onError: (_e, _v, ctx) => c.rollback(ctx),
    onSuccess: (tx, v) => c.set((s) => ({ ...s, transactions: upsert(s.transactions, tx, v.id ?? v.tmp) })),
  })
}

/** useSaveTransaction().mutate(...) uchun argument: yangi yozuvga vaqtinchalik id beradi. */
export const saveTransactionVars = (draft: TransactionDraft, id?: string) => ({ id, draft, tmp: tempId() })

export function useDeleteTransaction() {
  const c = cache(useQueryClient())
  return useMutation({
    mutationFn: ledgerService.deleteTransaction,
    onMutate: (id: string) => c.optimistic((s) => ({ ...s, transactions: s.transactions.filter((x) => x.id !== id) })),
    onError: (_e, _v, ctx) => c.rollback(ctx),
  })
}

export function useSaveDebt() {
  const c = cache(useQueryClient())
  return useMutation({
    mutationFn: (v: { id?: string; draft: DebtDraft; tmp: string }) => (v.id ? ledgerService.updateDebt(v.id, v.draft) : ledgerService.createDebt(v.draft)),
    onMutate: (v) => c.optimistic((s) => ({ ...s, debts: upsert(s.debts, { ...v.draft, id: v.id ?? v.tmp, createdAt: null }) })),
    onError: (_e, _v, ctx) => c.rollback(ctx),
    onSuccess: (debt, v) => c.set((s) => ({ ...s, debts: upsert(s.debts, debt, v.id ?? v.tmp) })),
  })
}

export const saveDebtVars = (draft: DebtDraft, id?: string) => ({ id, draft, tmp: tempId() })

export function useDeleteDebt() {
  const c = cache(useQueryClient())
  return useMutation({
    mutationFn: ledgerService.deleteDebt,
    onMutate: (id: string) => c.optimistic((s) => ({ ...s, debts: s.debts.filter((x) => x.id !== id) })),
    onError: (_e, _v, ctx) => c.rollback(ctx),
  })
}

/** To'lov server javobini kutadi: qoldiq va keyingi to'lov sanasini server hisoblaydi. */
export function usePayDebt() {
  const c = cache(useQueryClient())
  return useMutation({
    mutationFn: (v: { id: string; payment: DebtPayment }) => ledgerService.payDebt(v.id, v.payment),
    onSuccess: ({ debt, transaction }) =>
      c.set((s) => ({ ...s, debts: upsert(s.debts, debt), transactions: transaction ? upsert(s.transactions, transaction) : s.transactions })),
  })
}

export function useSavePlan() {
  const c = cache(useQueryClient())
  return useMutation({
    mutationFn: (v: { month: string; values: PlanValues }) => ledgerService.savePlan(v.month, v.values),
    onMutate: (v) => c.optimistic((s) => ({ ...s, plans: { ...s.plans, [v.month]: v.values } })),
    onError: (_e, _v, ctx) => c.rollback(ctx),
    onSuccess: (values, v) => c.set((s) => ({ ...s, plans: { ...s.plans, [v.month]: values } })),
  })
}

export function useCopyPreviousPlan() {
  const c = cache(useQueryClient())
  return useMutation({
    mutationFn: ledgerService.copyPreviousPlan,
    onSuccess: (values, month: string) => c.set((s) => ({ ...s, plans: { ...s.plans, [month]: values } })),
  })
}

export function useUpdateSettings() {
  const c = cache(useQueryClient())
  return useMutation({
    mutationFn: ledgerService.updateSettings,
    onMutate: (patch: Partial<LedgerSettings>) => c.optimistic((s) => ({ ...s, settings: { ...s.settings, ...patch } })),
    onError: (_e, _v, ctx) => c.rollback(ctx),
    onSuccess: (settings) => c.set((s) => ({ ...s, settings })),
  })
}

export function useExportExcel() {
  return useMutation({ mutationFn: ledgerService.exportExcel })
}
