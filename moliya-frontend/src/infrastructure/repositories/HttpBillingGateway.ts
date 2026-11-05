import type { BillingGateway, TelegramLogin } from "@/application/ports"
import type { Access, Account, Order, Prices } from "@/domain/types"
import { asciiJson, type HttpClient } from "../http/client"

/** To'lov sayti so'rovlari Telegram Login Widget imzosi bilan (X-Telegram-Login). */
export class HttpBillingGateway implements BillingGateway {
  constructor(private readonly http: HttpClient) {}

  private auth(login: TelegramLogin) {
    return { headers: { "X-Telegram-Login": asciiJson(login) } }
  }

  async prices() {
    return (await this.http.get<{ prices: Prices }>("billing/prices")).prices
  }
  siteMe(login: TelegramLogin) {
    return this.http.get<{ account: Account; access: Access; prices: Prices }>("billing/me", this.auth(login))
  }
  createOrder(login: TelegramLogin, months: number, provider: "payme" | "click") {
    return this.http.post<{ order: Order; payUrl: string }>("billing/orders", { months, provider }, this.auth(login))
  }
  sendInvoice(login: TelegramLogin, months: number, phone: string) {
    return this.http.post<{ order: Order; invoiceId: string }>("billing/invoices", { months, phone }, this.auth(login))
  }
  orderStatus(login: TelegramLogin, orderId: string) {
    return this.http.get<{ order: Order; access: Access }>(`billing/orders/${orderId}`, this.auth(login))
  }
}
