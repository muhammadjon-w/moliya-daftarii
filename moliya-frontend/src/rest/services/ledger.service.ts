// Hisob API'si: faqat HTTP chaqiruvlar, kesh va holat yo'q (ular queries/ ichida).
import type { DebtPaymentResult, LedgerState } from "@/types/api"
import type { Debt, DebtDraft, DebtPayment, LedgerSettings, PlanValues, Transaction, TransactionDraft } from "@/types/ledger"
import { api } from "../client"

export const ledgerService = {
  state: () => api.get<LedgerState>("ledger/state"),

  createTransaction: (d: TransactionDraft) => api.post<Transaction>("transactions", d),
  updateTransaction: (id: string, d: TransactionDraft) => api.put<Transaction>(`transactions/${id}`, d),
  deleteTransaction: (id: string) => api.delete(`transactions/${id}`),

  createDebt: (d: DebtDraft) => api.post<Debt>("debts", d),
  updateDebt: (id: string, d: DebtDraft) => api.put<Debt>(`debts/${id}`, d),
  deleteDebt: (id: string) => api.delete(`debts/${id}`),
  payDebt: (id: string, p: DebtPayment) => api.post<DebtPaymentResult>(`debts/${id}/payments`, p),

  savePlan: (month: string, values: PlanValues) => api.put<PlanValues>(`plans/${month}`, { values }),
  copyPreviousPlan: (month: string) => api.post<PlanValues>(`plans/${month}/copy-previous`),

  updateSettings: (patch: Partial<LedgerSettings>) => api.put<LedgerSettings>("settings", patch),
  /** Excel fayl bot chatiga yuboriladi. */
  exportExcel: (month: string) => api.post<{ filename: string }>("exports/excel", { month }),
}
