// Fetch ustidagi yupqa qatlam: manzil, autentifikatsiya sarlavhasi, xatolarni ApiError'ga aylantirish.
import { ApiError } from "@/application/errors"
import type { Access } from "@/domain/types"

export interface HttpClientOptions {
  baseUrl: string
  /** Har so'rovga qo'shiladigan sarlavhalar (masalan, Authorization: tma ...). */
  authHeaders: () => Record<string, string>
  timeoutMs?: number
}

export type RequestOptions = { body?: unknown; headers?: Record<string, string> }

export class HttpClient {
  constructor(private readonly opts: HttpClientOptions) {}

  get<T>(path: string, o?: RequestOptions) { return this.request<T>("GET", path, o) }
  post<T>(path: string, body?: unknown, o?: RequestOptions) { return this.request<T>("POST", path, { ...o, body }) }
  put<T>(path: string, body?: unknown, o?: RequestOptions) { return this.request<T>("PUT", path, { ...o, body }) }
  delete<T = void>(path: string, o?: RequestOptions) { return this.request<T>("DELETE", path, o) }

  async request<T>(method: string, path: string, o: RequestOptions = {}): Promise<T> {
    const ctrl = new AbortController()
    const timer = setTimeout(() => ctrl.abort(), this.opts.timeoutMs ?? 20_000)
    const headers: Record<string, string> = { Accept: "application/json", ...this.opts.authHeaders(), ...o.headers }
    if (o.body !== undefined) headers["Content-Type"] = "application/json"
    let res: Response
    try {
      res = await fetch(this.opts.baseUrl.replace(/\/$/, "") + "/" + path.replace(/^\//, ""), {
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
      const d = (data ?? {}) as { error?: string; message?: string; detail?: string; fields?: Record<string, string[]>; access?: Access }
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
