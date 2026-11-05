// TanStack Query kalitlari bir joyda: invalidatsiya va kesh yangilash shu kalitlar bo'yicha.
export const queryKeys = {
  ledger: ["ledger", "state"] as const,
  me: ["session", "me"] as const,
  prices: ["billing", "prices"] as const,
  siteMe: (userId: number | string) => ["billing", "site-me", userId] as const,
  order: (id: string) => ["billing", "order", id] as const,
}
