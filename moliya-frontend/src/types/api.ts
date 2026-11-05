// API javoblari shakli.
import type { Access, Account, Order, Prices } from "./account"
import type { Debt, LedgerSettings, Plans, Transaction } from "./ledger"

/** GET ledger/state — ilova ochilganda bitta so'rov. */
export interface LedgerState {
  account: Account | null
  access: Access
  transactions: Transaction[]
  debts: Debt[]
  plans: Plans
  settings: LedgerSettings
}

export interface DebtPaymentResult {
  debt: Debt
  transaction: Transaction | null
}

export interface SiteMe {
  account: Account
  access: Access
  prices: Prices
}

export interface CreatedOrder {
  order: Order
  payUrl: string
}

export interface OrderStatus {
  order: Order
  access: Access
}

/** Backend xatolari bitta formatda keladi. */
export interface ApiErrorBody {
  error?: string
  message?: string
  detail?: string
  fields?: Record<string, string[]>
  access?: Access
}
