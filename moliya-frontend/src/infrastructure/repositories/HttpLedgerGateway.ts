import type { LedgerGateway, SessionGateway } from "@/application/ports"
import type { Access, Account, Debt, DebtDraft, DebtPayment, LedgerSettings, LedgerState, PlanValues, Transaction, TransactionDraft } from "@/domain/types"
import type { HttpClient } from "../http/client"

export class HttpLedgerGateway implements LedgerGateway {
  constructor(private readonly http: HttpClient) {}

  state() { return this.http.get<LedgerState>("ledger/state") }
  createTransaction(d: TransactionDraft) { return this.http.post<Transaction>("transactions", d) }
  updateTransaction(id: string, d: TransactionDraft) { return this.http.put<Transaction>(`transactions/${id}`, d) }
  deleteTransaction(id: string) { return this.http.delete(`transactions/${id}`) }
  createDebt(d: DebtDraft) { return this.http.post<Debt>("debts", d) }
  updateDebt(id: string, d: DebtDraft) { return this.http.put<Debt>(`debts/${id}`, d) }
  deleteDebt(id: string) { return this.http.delete(`debts/${id}`) }
  payDebt(id: string, p: DebtPayment) { return this.http.post<{ debt: Debt; transaction: Transaction | null }>(`debts/${id}/payments`, p) }
  savePlan(month: string, values: PlanValues) { return this.http.put<PlanValues>(`plans/${month}`, { values }) }
  copyPreviousPlan(month: string) { return this.http.post<PlanValues>(`plans/${month}/copy-previous`) }
  updateSettings(patch: Partial<LedgerSettings>) { return this.http.put<LedgerSettings>("settings", patch) }
  exportExcel(month: string) { return this.http.post<{ filename: string }>("exports/excel", { month }) }
}

export class HttpSessionGateway implements SessionGateway {
  constructor(private readonly http: HttpClient) {}
  me() { return this.http.get<{ account: Account; access: Access }>("me") }
}
