// Foydalanuvchi, obuna va to'lov tiplari.

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
  lastName: string | null
  username: string | null
  languageCode: string | null
}

/** Muddat (oy) → narx (so'm), masalan { "1": 29000, "12": 249000 } */
export type Prices = Record<string, number>

export type PayProvider = "payme" | "click"

export interface Order {
  id: string
  months: number
  amount: number
  provider: PayProvider
  status: string
}

/** Telegram Login Widget qaytargan imzolangan ma'lumot (to'lov sayti uchun). */
export type TelegramLogin = Record<string, string | number>
