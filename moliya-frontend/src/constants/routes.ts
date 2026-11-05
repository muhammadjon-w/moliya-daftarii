// Sahifa nomlari. Router va navigatsiyada matn emas, shu konstantalar ishlatiladi.
export const ROUTES = {
  home: "home",
  records: "records",
  report: "report",
  debts: "debts",
  plan: "plan",
  subscribe: "subscribe",
} as const

export type RouteName = (typeof ROUTES)[keyof typeof ROUTES]
