// Fetch ustidagi yupqa qatlam: manzil, autentifikatsiya sarlavhasi, xatolarni ApiError'ga aylantirish.
// Komponentlar bu faylni to'g'ridan-to'g'ri ishlatmaydi: services → queries → komponent.
import { ENV, REQUEST_TIMEOUT_MS } from "@/constants/app"
import { telegram } from "@/plugins/telegram"
import type { Access } from "@/types/account"
import type { ApiErrorBody } from "@/types/api"

export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly code: string,
    message: string,
    readonly fields: Record<string, string[]> | null = null,
    readonly access: Access | null = null,
  ) {
    super(message)
    this.name = "ApiError"
  }

  /** Obuna tugagan: yozish taqiqlangan (402). */
  get subscriptionRequired(): boolean {
    return this.status === 402
  }

  get unauthorized(): boolean {
    return this.status === 401 || this.status === 403
  }

  /** 4xx — qayta urinishdan foyda yo'q. */
  get clientError(): boolean {
    return this.status >= 400 && this.status < 500
  }
}

export type RequestOptions = { body?: unknown; headers?: Record<string, string> }

export class HttpClient {
  constructor(
    private readonly baseUrl: string,
    private readonly authHeaders: () => Record<string, string>,
  ) {}

  get<T>(path: string, o?: RequestOptions) { return this.request<T>("GET", path, o) }
  post<T>(path: string, body?: unknown, o?: RequestOptions) { return this.request<T>("POST", path, { ...o, body }) }
  put<T>(path: string, body?: unknown, o?: RequestOptions) { return this.request<T>("PUT", path, { ...o, body }) }
  delete<T = void>(path: string, o?: RequestOptions) { return this.request<T>("DELETE", path, o) }

  async request<T>(method: string, path: string, o: RequestOptions = {}): Promise<T> {
    const ctrl = new AbortController()
    const timer = setTimeout(() => ctrl.abort(), REQUEST_TIMEOUT_MS)
    const headers: Record<string, string> = { Accept: "application/json", ...this.authHeaders(), ...o.headers }
    if (o.body !== undefined) headers["Content-Type"] = "application/json"
    let res: Response
    try {
      res = await fetch(this.baseUrl.replace(/\/$/, "") + "/" + path.replace(/^\//, ""), {
        method,
        headers,
        body: o.body === undefined ? undefined : JSON.stringify(o.body),
        signal: ctrl.signal,
      })
    } catch (e) {
      const aborted = e instanceof DOMException && e.name === "AbortError"
      throw new ApiError(0, aborted ? "timeout" : "network", aborted ? "Server javob bermadi" : "Internet aloqasini tekshiring")
    } finally {
      clearTimeout(timer)
    }
    if (res.status === 204) return undefined as T
    const text = await res.text()
    let data: unknown = null
    try {
      data = text ? JSON.parse(text) : null
    } catch {
      data = null
    }
    if (!res.ok) {
      const d = (data ?? {}) as ApiErrorBody
      throw new ApiError(res.status, d.error ?? "http_" + res.status, d.message ?? d.detail ?? res.statusText, d.fields ?? null, d.access ?? null)
    }
    return data as T
  }
}

/**
 * HTTP sarlavhalar faqat ASCII bo'lishi kerak. Login Widget ma'lumotida kirill/o'zbek ism bo'lishi mumkin,
 * shuning uchun ASCII bo'lmagan belgilar \uXXXX ko'rinishida yoziladi (JSON buni o'zi o'qiydi).
 */
export function asciiJson(v: unknown): string {
  return JSON.stringify(v).replace(/[\u007f-￿]/g, (c) => "\\u" + c.charCodeAt(0).toString(16).padStart(4, "0"))
}

function miniAppAuth(): Record<string, string> {
  if (telegram.initData) return { Authorization: "tma " + telegram.initData }
  // Faqat lokal ishlab chiqishda: Telegram'siz brauzerda ochish (server ham DEBUG rejimida bo'lishi shart)
  if (ENV.devUserId) return { "X-Dev-User-Id": String(ENV.devUserId) }
  return {}
}

/** Mini app so'rovlari (Telegram initData bilan). */
export const api = new HttpClient(ENV.apiBaseUrl, miniAppAuth)
/** To'lov sayti so'rovlari: imzo har so'rovda X-Telegram-Login sarlavhasida alohida beriladi. */
export const siteApi = new HttpClient(ENV.apiBaseUrl, () => ({}))
