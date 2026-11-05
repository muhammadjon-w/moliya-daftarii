// Interfeys holati tiplari (server ma'lumoti emas).
import type { Debt, Transaction, TxType } from "./ledger"

export type Lang = "uz" | "ru" | "en"

/** Ikonka va kartochkalar rangi. Qiymatlar styles/tokens.css dagi --tone-* o'zgaruvchilariga mos. */
export type Tone = "teal" | "red" | "yellow" | "blue" | "orange" | "purple" | "pink"

/** Bir vaqtda faqat bitta pastki oyna (bottom sheet) ochiq bo'ladi. */
export type Sheet =
  | { kind: "record"; type: TxType; tx?: Transaction }
  | { kind: "debt"; debt?: Debt }
  | { kind: "pay"; debt: Debt }
  | { kind: "settings" }
  | { kind: "month" }

export interface Toast {
  id: number
  text: string
  error: boolean
}
