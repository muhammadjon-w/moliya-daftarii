// TanStack Query kalitlari. Kalitni faqat shu yerdan oling — qo'lda massiv yozmang.
export const queryKeys = {
  ledger: ["ledger", "state"] as const,
  prices: ["billing", "prices"] as const,
  siteMe: (userId: string | number) => ["billing", "me", userId] as const,
  order: (id: string) => ["billing", "order", id] as const,
}
