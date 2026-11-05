// Hisob tiplari. Backend JSON'i (camelCase) bilan bir xil shakl.

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

export interface Period {
  y: number
  /** 0..11 */
  m: number
}
