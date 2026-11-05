// Kompozitsiya ildizi: portlarni aniq amalga oshirishlar bilan ulaydi. Faqat shu fayl infrastructure'ni biladi.
import type { Gateways } from "@/application/ports"
import { HttpClient } from "@/infrastructure/http/client"
import { HttpBillingGateway } from "@/infrastructure/repositories/HttpBillingGateway"
import { HttpLedgerGateway, HttpSessionGateway } from "@/infrastructure/repositories/HttpLedgerGateway"
import { createTelegramPlatform, telegramInitData } from "@/infrastructure/telegram/webapp"

export function createGateways(env: ImportMetaEnv = import.meta.env): Gateways {
  const baseUrl = env.VITE_API_BASE_URL || "/api/v1"
  const devUserId = env.DEV ? env.VITE_DEV_USER_ID : undefined

  const http = new HttpClient({
    baseUrl,
    authHeaders(): Record<string, string> {
      const initData = telegramInitData()
      if (initData) return { Authorization: "tma " + initData }
      // Faqat lokal ishlab chiqishda: Telegram'siz brauzerda ochish (server ham DEBUG rejimida bo'lishi shart)
      if (devUserId) return { "X-Dev-User-Id": String(devUserId) }
      return {}
    },
  })
  const siteHttp = new HttpClient({ baseUrl, authHeaders: () => ({}) })

  return {
    ledger: new HttpLedgerGateway(http),
    session: new HttpSessionGateway(http),
    billing: new HttpBillingGateway(siteHttp),
    platform: createTelegramPlatform(),
  }
}
