// Telegram WebApp SDK adapteri (Platform porti). SDK index.html'da <script> orqali yuklanadi.
import type { Platform } from "@/application/ports"

interface TgWebApp {
  initData: string
  initDataUnsafe?: { user?: { first_name?: string; language_code?: string } }
  ready(): void
  expand(): void
  setHeaderColor?(c: string): void
  setBackgroundColor?(c: string): void
  openLink(url: string): void
  showConfirm?(msg: string, cb: (ok: boolean) => void): void
  HapticFeedback?: { notificationOccurred(t: "success" | "error" | "warning"): void; impactOccurred(s: "light" | "medium"): void }
  isVersionAtLeast?(v: string): boolean
}

function sdk(): TgWebApp | null {
  const w = window as unknown as { Telegram?: { WebApp?: TgWebApp } }
  const app = w.Telegram?.WebApp
  // SDK Telegram tashqarisida ham yuklanadi, lekin initData bo'sh bo'ladi
  return app && app.initData ? app : null
}

/** Mini app ichida bo'lsa: imzolangan initData (server shuni tekshiradi). */
export function telegramInitData(): string | null {
  return sdk()?.initData ?? null
}

export function createTelegramPlatform(): Platform {
  const app = sdk()
  const user = app?.initDataUnsafe?.user
  return {
    insideTelegram: !!app,
    userFirstName: user?.first_name ?? null,
    languageCode: user?.language_code ?? null,
    ready() {
      if (!app) return
      app.ready()
      app.expand()
      try {
        app.setHeaderColor?.("#0B1325")
        app.setBackgroundColor?.("#0B1325")
      } catch {
        /* eski Telegram versiyalari */
      }
    },
    haptic(kind) {
      const h = app?.HapticFeedback
      if (!h) return
      if (kind === "light") h.impactOccurred("light")
      else h.notificationOccurred(kind)
    },
    openLink(url) {
      if (app) app.openLink(url)
      else window.open(url, "_blank", "noopener")
    },
    confirm(message) {
      if (app?.showConfirm && app.isVersionAtLeast?.("6.2")) return new Promise((r) => app.showConfirm!(message, r))
      return Promise.resolve(window.confirm(message))
    },
  }
}
