// Telegram WebApp SDK adapteri. SDK index.html'da <script> orqali yuklanadi.
// Ilovaning qolgan qismi Telegram'ni faqat shu fayl (va composables/useTelegram) orqali biladi.
import { THEME_BG } from "@/constants/app"

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
  const app = (window as unknown as { Telegram?: { WebApp?: TgWebApp } }).Telegram?.WebApp
  // SDK Telegram tashqarisida ham yuklanadi, lekin initData bo'sh bo'ladi
  return app && app.initData ? app : null
}

const app = sdk()
const user = app?.initDataUnsafe?.user

export const telegram = {
  insideTelegram: !!app,
  /** Imzolangan initData: har bir API so'rovida "Authorization: tma ..." sarlavhasida yuboriladi. */
  initData: app?.initData ?? null,
  firstName: user?.first_name ?? null,
  languageCode: user?.language_code ?? null,

  ready() {
    if (!app) return
    app.ready()
    app.expand()
    try {
      app.setHeaderColor?.(THEME_BG)
      app.setBackgroundColor?.(THEME_BG)
    } catch {
      /* eski Telegram versiyalari */
    }
  },
  haptic(kind: "success" | "error" | "light") {
    const h = app?.HapticFeedback
    if (!h) return
    if (kind === "light") h.impactOccurred("light")
    else h.notificationOccurred(kind)
  },
  openLink(url: string) {
    if (app) app.openLink(url)
    else window.open(url, "_blank", "noopener")
  },
  confirm(message: string): Promise<boolean> {
    if (app?.showConfirm && app.isVersionAtLeast?.("6.2")) return new Promise((r) => app.showConfirm!(message, r))
    return Promise.resolve(window.confirm(message))
  },
}

export type Telegram = typeof telegram
