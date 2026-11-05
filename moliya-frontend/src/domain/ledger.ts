// Hisob-kitob qoidalari: oylik yig'indilar, jamg'arma, qarz qoldig'i, hisobot.
// Sof funksiyalar: Vue, so'rovlar va DOM'ni bilmaydi, shuning uchun alohida test qilinadi.
import { EXPENSE_GROUPS, METHODS, categoriesOfGroup } from "./catalog"
import { monthKey, shiftMonth } from "./money"
import type { Debt, DebtStatus, Group, Method, PlanValues, Transaction } from "./types"

export const DEFAULT_USD_RATE = 12000

export function groupOf(x: Pick<Transaction, "type" | "group">): Group {
  if (x.type === "income") return "inc"
  return (EXPENSE_GROUPS as readonly string[]).includes(x.group) ? x.group : "exp"
}

export function toUzs(x: Pick<Transaction, "amount" | "currency">, usdRate: number): number {
  return x.currency === "USD" ? x.amount * usdRate : x.amount
}

export function monthTransactions(all: readonly Transaction[], y: number, m: number): Transaction[] {
  const k = monthKey(y, m)
  return all.filter((x) => x.date.slice(0, 7) === k)
}

export interface Totals {
  inc: number
  pay: number
  exp: number
  debt: number
  out: number
  net: number
  incUsd: number
  outUsd: number
}

export function totals(list: readonly Transaction[], usdRate: number): Totals {
  const r = { inc: 0, pay: 0, exp: 0, debt: 0, incUsd: 0, outUsd: 0 }
  for (const x of list) {
    const g = groupOf(x)
    r[g] += toUzs(x, usdRate)
    if (x.currency === "USD") {
      if (g === "inc") r.incUsd += x.amount
      else r.outUsd += x.amount
    }
  }
  const out = r.pay + r.exp + r.debt
  return { ...r, out, net: r.inc - out }
}

/** Oy boshidagi qoldiq: boshlang'ich qoldiq + oldingi barcha oylar sof natijasi. */
export function balanceBefore(all: readonly Transaction[], y: number, m: number, usdRate: number, openingBalance: number): number {
  const k = monthKey(y, m)
  let s = openingBalance || 0
  for (const x of all) if (x.date.slice(0, 7) < k) s += (x.type === "income" ? 1 : -1) * toUzs(x, usdRate)
  return s
}

/** Kun bo'yicha yig'ilib boruvchi summa (sparkline uchun). Joriy oyda bugungi kungacha. */
export function dailyCumulative(list: readonly Transaction[], y: number, m: number, usdRate: number, pred: (x: Transaction) => boolean, now = new Date()): number[] {
  const dim = new Date(y, m + 1, 0).getDate()
  const last = now.getFullYear() === y && now.getMonth() === m ? now.getDate() : dim
  const arr = new Array<number>(last).fill(0)
  for (const x of list) {
    if (!pred(x)) continue
    const d = Number(x.date.slice(8, 10)) || 1
    if (d <= last) arr[d - 1] += toUzs(x, usdRate)
  }
  for (let i = 1; i < arr.length; i++) arr[i] += arr[i - 1]
  return arr
}

// ---------- qarzlar ----------
export interface DebtCalc {
  principal: number
  paid: number
  remaining: number
  months: number
  monthly: number
  status: Exclude<DebtStatus, "">
}

export function debtCalc(d: Pick<Debt, "principal" | "paid" | "months"> & Partial<Pick<Debt, "status" | "deadline">>, today: string): DebtCalc {
  const principal = Number(d.principal) || 0
  const paid = Number(d.paid) || 0
  const remaining = Math.max(principal - paid, 0)
  const months = Number(d.months) || 0
  const monthly = months > 0 ? remaining / months : 0
  const status: DebtCalc["status"] = d.status || (remaining <= 0 ? "paid" : d.deadline && d.deadline < today ? "overdue" : "active")
  return { principal, paid, remaining, months, monthly, status }
}

export interface DebtSummary {
  principal: number
  paid: number
  remaining: number
  monthly: number
  openCount: number
}

export function debtSummary(debts: readonly Debt[], today: string): DebtSummary {
  const s = { principal: 0, paid: 0, remaining: 0, monthly: 0, openCount: 0 }
  for (const d of debts) {
    const c = debtCalc(d, today)
    s.principal += c.principal
    s.paid += c.paid
    s.remaining += c.remaining
    if (c.remaining > 0) s.openCount++
    if (c.status !== "paid") s.monthly += c.monthly
  }
  return s
}

/** Yaqin to'lov sanasi bo'yicha ochiq qarzlar. */
export function upcomingDebts(debts: readonly Debt[], today: string, limit = 5): { debt: Debt; calc: DebtCalc }[] {
  return debts
    .map((debt) => ({ debt, calc: debtCalc(debt, today) }))
    .filter((o) => o.calc.remaining > 0)
    .sort((a, b) => String(a.debt.payDate || a.debt.deadline || "9999").localeCompare(String(b.debt.payDate || b.debt.deadline || "9999")))
    .slice(0, limit)
}

export interface DebtBuckets {
  overdue: number
  d30: number
  d60: number
  later: number
  total: number
}

export function debtBuckets(debts: readonly Debt[], today: string): DebtBuckets {
  const b = { overdue: 0, d30: 0, d60: 0, later: 0, total: 0 }
  const t0 = Date.parse(today)
  for (const d of debts) {
    const c = debtCalc(d, today)
    if (c.remaining <= 0) continue
    b.total += c.remaining
    const due = d.payDate || d.deadline
    const days = due ? (Date.parse(due) - t0) / 864e5 : NaN
    if (Number.isNaN(days) || days > 60) b.later += c.remaining
    else if (days < 0) b.overdue += c.remaining
    else if (days <= 30) b.d30 += c.remaining
    else b.d60 += c.remaining
  }
  return b
}

// ---------- toifalar va moddalar ----------
export interface Share {
  key: string
  value: number
  group: Group
}

function sumBy(list: readonly Transaction[], usdRate: number, key: (x: Transaction) => string, pred: (x: Transaction) => boolean): Share[] {
  const map = new Map<string, Share>()
  for (const x of list) {
    if (!pred(x)) continue
    const k = key(x)
    const s = map.get(k) ?? { key: k, value: 0, group: groupOf(x) }
    s.value += toUzs(x, usdRate)
    map.set(k, s)
  }
  return [...map.values()].sort((a, b) => b.value - a.value)
}

export const byCategory = (list: readonly Transaction[], usdRate: number, income: boolean) =>
  sumBy(list, usdRate, (x) => x.category || "—", (x) => (x.type === "income") === income)

export const byItem = (list: readonly Transaction[], usdRate: number, income: boolean) =>
  sumBy(list, usdRate, (x) => x.item || x.category || "—", (x) => (x.type === "income") === income)

// ---------- yil ----------
export interface YearRow {
  m: number
  totals: Totals
  /** Oy oxiridagi jamg'arma */
  end: number
}

export function yearRows(all: readonly Transaction[], y: number, usdRate: number, openingBalance: number): YearRow[] {
  let running = balanceBefore(all, y, 0, usdRate, openingBalance)
  return Array.from({ length: 12 }, (_, m) => {
    const t = totals(monthTransactions(all, y, m), usdRate)
    running += t.net
    return { m, totals: t, end: running }
  })
}

// ---------- reja ----------
export interface PlanRow {
  category: string
  key: string
  plan: number
  fact: number
  /** Daromadda fakt − reja, chiqimda reja − fakt: musbat bo'lsa yaxshi. */
  diff: number
}

export interface PlanSection {
  group: Group
  rows: PlanRow[]
  plan: number
  fact: number
  diff: number
}

export function planSections(list: readonly Transaction[], plan: PlanValues, usdRate: number): PlanSection[] {
  return (["inc", ...EXPENSE_GROUPS] as Group[]).map((g) => {
    const cats = categoriesOfGroup(g)
    for (const x of list) if (groupOf(x) === g && x.category && !cats.includes(x.category)) cats.push(x.category)
    const isInc = g === "inc"
    const rows = cats.map((c) => {
      const key = `${g}:${c}`
      const p = Number(plan[key]) || 0
      let f = 0
      for (const x of list) if (groupOf(x) === g && x.category === c) f += toUzs(x, usdRate)
      return { category: c, key, plan: p, fact: f, diff: isInc ? f - p : p - f }
    })
    const sp = rows.reduce((s, r) => s + r.plan, 0)
    const sf = rows.reduce((s, r) => s + r.fact, 0)
    return { group: g, rows, plan: sp, fact: sf, diff: isInc ? sf - sp : sp - sf }
  })
}

export interface PlanOverview {
  income: number
  outflow: number
  overruns: { category: string; over: number }[]
}

export function planOverview(list: readonly Transaction[], plan: PlanValues, usdRate: number): PlanOverview {
  let income = 0
  let outflow = 0
  const overruns: { category: string; over: number }[] = []
  for (const [k, raw] of Object.entries(plan)) {
    const v = Number(raw) || 0
    const g = k.split(":")[0]
    const c = k.slice(g.length + 1)
    if (g === "inc") {
      income += v
      continue
    }
    outflow += v
    let f = 0
    for (const x of list) if (groupOf(x) === g && x.category === c) f += toUzs(x, usdRate)
    if (v > 0 && f > v) overruns.push({ category: c, over: f - v })
  }
  overruns.sort((a, b) => b.over - a.over)
  return { income, outflow, overruns }
}

// ---------- kassa ----------
export interface CashRow {
  start: number
  inflow: number
  outflow: number
  end: number
}

export interface CashReport {
  byMethod: { method: Method; row: CashRow }[]
  total: CashRow
  /** Dollardagi yozuvlar alohida, dollarda */
  usd: CashRow | null
}

export function cashReport(all: readonly Transaction[], y: number, m: number): CashReport {
  const k0 = monthKey(y, m)
  const mk = () => ({ start: 0, inflow: 0, outflow: 0, end: 0 })
  const rows = new Map<Method, CashRow>(METHODS.map((x) => [x, mk()]))
  const usd = mk()
  for (const x of all) {
    const k = x.date.slice(0, 7)
    const sign = x.type === "income" ? 1 : -1
    const r = x.currency === "USD" ? usd : rows.get(x.method) ?? rows.get("cash")!
    if (k < k0) r.start += sign * x.amount
    else if (k === k0) {
      if (sign > 0) r.inflow += x.amount
      else r.outflow += x.amount
    }
  }
  const fin = (r: CashRow) => ({ ...r, end: r.start + r.inflow - r.outflow })
  const byMethod = METHODS.map((method) => ({ method, row: fin(rows.get(method)!) }))
  const total = fin(byMethod.reduce((z, { row }) => ({ start: z.start + row.start, inflow: z.inflow + row.inflow, outflow: z.outflow + row.outflow, end: 0 }), mk()))
  return { byMethod, total, usd: usd.start || usd.inflow || usd.outflow ? fin(usd) : null }
}

/** O'tgan oyga nisbatan o'zgarish foizi; o'tgan oy bo'sh bo'lsa null. */
export function changePct(value: number, previous: number): number | null {
  return previous ? Math.round(((value - previous) / previous) * 100) : null
}

export function previousMonth(y: number, m: number) {
  return shiftMonth(y, m, -1)
}
