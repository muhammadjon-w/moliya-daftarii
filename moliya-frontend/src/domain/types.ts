// Domen tiplari. Backend JSON'i (camelCase) bilan bir xil shakl.

export type TxType = "income" | "expense"
export type ExpenseGroup = "pay" | "exp" | "debt"
export type Group = "inc" | ExpenseGroup
export type Currency = "UZS" | "USD"
export type Method = "cash" | "card" | "bank"
export type DebtStatus = "" | "active" | "paid" | "overdue"

export interface Transaction {
  id: string
  type: TxType
  group: Group
  item: string
  category: string
  amount: number
  currency: Currency
  /** YYYY-MM-DD */
  date: string
  method: Method
  note: string
  createdAt: string | null
}

export type TransactionDraft = Omit<Transaction, "id" | "createdAt">

export interface Debt {
  id: string
  lender: string
  principal: number
  paid: number
  months: number
  status: DebtStatus
  date: string | null
  payDate: string | null
  deadline: string | null
  note: string
  createdAt: string | null
}

export type DebtDraft = Omit<Debt, "id" | "createdAt">

export interface DebtPayment {
  amount: number
  date: string
  logTransaction: boolean
}

/** Kalit: "inc:salary", "exp:food" ...; qiymat: so'm */
export type PlanValues = Record<string, number>
/** Kalit: "YYYY-MM" */
export type Plans = Record<string, PlanValues>

export interface LedgerSettings {
  usdRate: number
  openingBalance: number
}

export type AccessState = "trial" | "active" | "expired"

export interface Access {
  state: AccessState
  trialEndsAt: string
  paidUntil: string | null
  daysLeft: number
  canWrite: boolean
}

export interface Account {
  id: number
  firstName: string
  lastName: string
  username: string
  languageCode: string
}

export interface LedgerState {
  access: Access
  transactions: Transaction[]
  debts: Debt[]
  plans: Plans
  settings: LedgerSettings
}

export interface Period {
  y: number
  /** 0..11 */
  m: number
}

export type Prices = Record<string, number>

export interface Order {
  id: string
  months: number
  amount: number
  provider: "payme" | "click"
  status: string
}
