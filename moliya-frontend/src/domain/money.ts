// Pul va sanalarni formatlash. Sof funksiyalar, DOM va Vue'ni bilmaydi.

const NBSP = " "

/** 10 000 000 ko'rinishida, kasrsiz. */
export function num(n: number): string {
  return Math.round(n).toLocaleString("ru-RU").replace(/\s/g, NBSP)
}

export function signed(n: number): string {
  return (n < 0 ? "−" : "") + num(Math.abs(n))
}

export function usd(n: number): string {
  return "$" + NBSP + num(n)
}

/** Kiritish maydoni uchun: 10 000 000 yoki 1 250,5. Nol bo'sh satr. */
export function formatInput(n: number): string {
  if (!Number.isFinite(n) || n === 0) return ""
  const neg = n < 0
  const [int, dec] = String(Math.round(Math.abs(n) * 100) / 100).split(".")
  return (neg ? "-" : "") + int.replace(/\B(?=(\d{3})+(?!\d))/g, " ") + (dec ? "," + dec : "")
}

/** "10 000 000,5" → 10000000.5; noto'g'ri bo'lsa NaN. */
export function parseMoney(v: unknown): number {
  const s = String(v ?? "").replace(/[\s ]/g, "").replace(",", ".")
  if (!s) return NaN
  const n = Number.parseFloat(s)
  return Number.isFinite(n) ? n : NaN
}

/** Foydalanuvchi yozayotgan matnni probellar bilan qayta yozadi. */
export function reformatTyping(raw: string, allowNegative = false): string {
  const neg = allowNegative && /^\s*-/.test(raw)
  const clean = raw.replace(/[^0-9.,]/g, "").replace(/\./g, ",")
  const i = clean.indexOf(",")
  let int = i >= 0 ? clean.slice(0, i) : clean
  const dec = i >= 0 ? clean.slice(i + 1).replace(/,/g, "").slice(0, 2) : null
  int = int.replace(/^0+(?=\d)/, "")
  return (neg ? "-" : "") + int.replace(/\B(?=(\d{3})+(?!\d))/g, " ") + (dec != null ? "," + dec : "")
}

export type CompactUnits = { billion: string; million: string; decimal: string }

/** 14,2 mln — KPI kartochkalari uchun. */
export function compact(n: number, u: CompactUnits): string {
  const a = Math.abs(n)
  const sign = n < 0 ? "−" : ""
  const f = (v: number) => String(Math.round(v * 10) / 10).replace(".", u.decimal)
  if (a >= 1e9) return sign + f(a / 1e9) + " " + u.billion
  if (a >= 1e6) return sign + (a >= 1e8 ? String(Math.round(a / 1e6)) : f(a / 1e6)) + " " + u.million
  return sign + num(a)
}

/** Diagramma o'qi uchun qisqa yozuv. */
export function axisLabel(n: number): string {
  const a = Math.abs(n)
  if (a >= 1e9) return (n / 1e9).toFixed(1).replace(/\.0$/, "") + " mlrd"
  if (a >= 1e6) return (n / 1e6).toFixed(1).replace(/\.0$/, "") + " mln"
  if (a >= 1e3) return Math.round(n / 1e3) + " ming"
  return String(Math.round(n))
}

const pad = (n: number) => (n < 10 ? "0" : "") + n

/** 2026-11 */
export function monthKey(y: number, m: number): string {
  return y + "-" + pad(m + 1)
}

export function todayIso(d = new Date()): string {
  return d.getFullYear() + "-" + pad(d.getMonth() + 1) + "-" + pad(d.getDate())
}

/** 2026-11-05 → 05.11.2026 */
export function fmtDate(d: string | null | undefined): string {
  const p = String(d ?? "").split("-")
  return p.length === 3 ? `${p[2]}.${p[1]}.${p[0]}` : d || "—"
}

export function shiftMonth(y: number, m: number, delta: number): { y: number; m: number } {
  const d = new Date(y, m + delta, 1)
  return { y: d.getFullYear(), m: d.getMonth() }
}

export function initials(s: string): string {
  const p = String(s || "?").trim().split(/\s+/)
  return ((p[0] || "?").charAt(0) + (p[1] ? p[1].charAt(0) : "")).toUpperCase()
}
