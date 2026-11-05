// Portlar: application qatlami tashqi dunyoni faqat shu interfeyslar orqali ko'radi.
// Amalga oshirishlar infrastructure/ ichida, bog'lash app/container.ts da.
import type {
  Access, Account, Debt, DebtDraft, DebtPayment, LedgerSettings, LedgerState, Order, PlanValues, Prices, Transaction, TransactionDraft,
} from "@/domain/types"

export interface LedgerGateway {
  state(): Promise<LedgerState>
  createTransaction(draft: TransactionDraft): Promise<Transaction>
  updateTransaction(id: string, draft: TransactionDraft): Promise<Transaction>
  deleteTransaction(id: string): Promise<void>
  createDebt(draft: DebtDraft): Promise<Debt>
  updateDebt(id: string, draft: DebtDraft): Promise<Debt>
  deleteDebt(id: string): Promise<void>
  payDebt(id: string, payment: DebtPayment): Promise<{ debt: Debt; transaction: Transaction | null }>
  savePlan(month: string, values: PlanValues): Promise<PlanValues>
  copyPreviousPlan(month: string): Promise<PlanValues>
  updateSettings(patch: Partial<LedgerSettings>): Promise<LedgerSettings>
  exportExcel(month: string): Promise<{ filename: string }>
}

export interface SessionGateway {
  me(): Promise<{ account: Account; access: Access }>
}

/** Telegram Login Widget qaytargan ma'lumot (to'lov sayti uchun). */
export type TelegramLogin = Record<string, string | number>

export interface BillingGateway {
  prices(): Promise<Prices>
  siteMe(login: TelegramLogin): Promise<{ account: Account; access: Access; prices: Prices }>
  createOrder(login: TelegramLogin, months: number, provider: "payme" | "click"): Promise<{ order: Order; payUrl: string }>
  sendInvoice(login: TelegramLogin, months: number, phone: string): Promise<{ order: Order; invoiceId: string }>
  orderStatus(login: TelegramLogin, orderId: string): Promise<{ order: Order; access: Access }>
}

/** Ilova qayerda ochilgani (Telegram yoki brauzer) — shu port orqali. */
export interface Platform {
  readonly insideTelegram: boolean
  readonly userFirstName: string | null
  readonly languageCode: string | null
  ready(): void
  haptic(kind: "success" | "error" | "light"): void
  openLink(url: string): void
  confirm(message: string): Promise<boolean>
}

export interface Gateways {
  ledger: LedgerGateway
  session: SessionGateway
  billing: BillingGateway
  platform: Platform
}
