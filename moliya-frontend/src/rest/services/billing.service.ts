// To'lov API'si. Sayt so'rovlari Telegram Login Widget imzosi bilan (X-Telegram-Login).
import type { PayProvider, Prices, TelegramLogin } from "@/types/account"
import type { CreatedOrder, OrderStatus, SiteMe } from "@/types/api"
import { asciiJson, siteApi } from "../client"

const auth = (login: TelegramLogin) => ({ headers: { "X-Telegram-Login": asciiJson(login) } })

export const billingService = {
  prices: async () => (await siteApi.get<{ prices: Prices }>("billing/prices")).prices,
  siteMe: (login: TelegramLogin) => siteApi.get<SiteMe>("billing/me", auth(login)),
  createOrder: (login: TelegramLogin, months: number, provider: PayProvider) =>
    siteApi.post<CreatedOrder>("billing/orders", { months, provider }, auth(login)),
  sendInvoice: (login: TelegramLogin, months: number, phone: string) =>
    siteApi.post<{ order: OrderStatus["order"]; invoiceId: string }>("billing/invoices", { months, phone }, auth(login)),
  orderStatus: (login: TelegramLogin, orderId: string) => siteApi.get<OrderStatus>(`billing/orders/${orderId}`, auth(login)),
}
