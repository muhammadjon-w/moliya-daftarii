// Hisob-kitob qoidalari: oylik yig'indilar, qoldiq, qarzlar, hisobot, reja.
// Sof funksiyalar: Vue, so'rovlar va DOM'ni bilmaydi — tests/ ichida alohida tekshiriladi.
import { EXPENSE_GROUPS, categoriesOfGroup } from "@/constants/catalog"
import type { Debt, DebtStatus, ExpenseGroup, Group, PlanValues, Transaction } from "@/types/ledger"
import { daysBetween, monthKey } from "./money"

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

/** Yangi sana birinchi; bir kunda — keyin qo'shilgani birinchi. */
export function sortNewestFirst(list: readonly Transaction[]): Transaction[] {
  return [...list].sort((a, b) => b.date.localeCompare(a.date) || String(b.createdAt ?? "~").localeCompare(String(a.createdAt ?? "~")))
}

export interface Totals {
  inc: number
  pay: number
  exp: number
  debt: number
  /** pay + exp + debt */
  out: number
  /** inc − out */
  net: number
}

export function totals(list: readonly Transaction[], usdRate: number): Totals {
  const r = { inc: 0, pay: 0, exp: 0, debt: 0 }
  for (const x of list) r[groupOf(x)] += toUzs(x, usdRate)
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

/** Foiz (butun son); asos 0 bo'lsa null. */
export function percent(part: number, whole: number): number | null {
  return whole ? Math.round((part / whole) * 100) : null
}

/** O'tgan oyga nisbatan o'zgarish foizi; o'tgan oy bo'sh bo'lsa null. */
export function changePct(value: number, previous: number): number | null {
  return previous ? Math.round(((value - previous) / previous) * 100) : null
}

// ---------- hisobot ----------
export interface GroupShare {
  group: ExpenseGroup
  value: number
  /** Chiqimdagi ulushi, 0..100. Yig'indisi aniq 100 bo'lishi uchun oxirgisi to'ldiriladi. */
  pct: number
}

export function expenseShares(t: Totals): GroupShare[] {
  if (t.out <= 0) return []
  const rows = EXPENSE_GROUPS.map((group) => ({ group, value: t[group], pct: Math.round((t[group] / t.out) * 100) })).filter((r) => r.value > 0)
  const diff = 100 - rows.reduce((s, r) => s + r.pct, 0)
  if (rows.length && diff) rows.reduce((a, b) => (b.value > a.value ? b : a)).pct += diff
  return rows
}

export interface ItemSum {
  item: string
  category: string
  group: Group
  value: number
}

/** Modda bo'yicha yig'indi, kattasidan kichigiga. */
export function topItems(list: readonly Transaction[], usdRate: number, income: boolean, limit = 5): ItemSum[] {
  const map = new Map<string, ItemSum>()
  for (const x of list) {
    if ((x.type === "income") !== income) continue
    const key = x.item || x.category
    const s = map.get(key) ?? { item: key, category: x.category, group: groupOf(x), value: 0 }
    s.value += toUzs(x, usdRate)
    map.set(key, s)
  }
  return [...map.values()].sort((a, b) => b.value - a.value).slice(0, limit)
}

// ---------- reja ----------
export interface PlanRow {
  key: string
  group: Group
  category: string
  plan: number
  fact: number
}

/** Guruhdagi barcha toifalar (katalog + shu oyda ishlatilgan boshqalari) reja va fakt bilan. */
export function planRows(list: readonly Transaction[], plan: PlanValues, usdRate: number, group: Group): PlanRow[] {
  const cats = categoriesOfGroup(group)
  for (const x of list) if (groupOf(x) === group && x.category && !cats.includes(x.category)) cats.push(x.category)
  return cats.map((category) => {
    const key = `${group}:${category}`
    let fact = 0
    for (const x of list) if (groupOf(x) === group && x.category === category) fact += toUzs(x, usdRate)
    return { key, group, category, plan: Number(plan[key]) || 0, fact }
  })
}

export type PlanStatus =
  | { kind: "over"; amount: number }
  | { kind: "left"; amount: number }
  | { kind: "done" }
  | { kind: "progress"; pct: number }

/** Chiqimda: oshib ketdimi yoki qancha qoldi. Tushumda: necha foiz bajarildi. */
export function planStatus(r: Pick<PlanRow, "group" | "plan" | "fact">): PlanStatus {
  if (r.group === "inc") {
    const pct = percent(r.fact, r.plan) ?? 0
    return pct >= 100 ? { kind: "done" } : { kind: "progress", pct }
  }
  return r.fact > r.plan ? { kind: "over", amount: r.fact - r.plan } : { kind: "left", amount: r.plan - r.fact }
}

/** Rejasi bor qatorlar: avval oshib ketganlar, keyin kattasidan kichigiga. */
export function plannedRows(list: readonly Transaction[], plan: PlanValues, usdRate: number): PlanRow[] {
  const rows = (["inc", ...EXPENSE_GROUPS] as Group[]).flatMap((g) => planRows(list, plan, usdRate, g)).filter((r) => r.plan > 0)
  const over = (r: PlanRow) => (r.group !== "inc" && r.fact > r.plan ? 1 : 0)
  return rows.sort((a, b) => over(b) - over(a) || b.plan - a.plan)
}

// ---------- qarzlar ----------
export interface DebtCalc {
  principal: number
  paid: number
  remaining: number
  months: number
  monthly: number
  status: Exclude<DebtStatus, "">
  /** To'langan qismi, 0..100 */
  paidPct: number
}

export function debtCalc(d: Pick<Debt, "principal" | "paid" | "months"> & Partial<Pick<Debt, "status" | "deadline">>, today: string): DebtCalc {
  const principal = Number(d.principal) || 0
  const paid = Number(d.paid) || 0
  const remaining = Math.max(principal - paid, 0)
  const months = Number(d.months) || 0
  const monthly = months > 0 ? remaining / months : 0
  const status: DebtCalc["status"] = d.status || (remaining <= 0 ? "paid" : d.deadline && d.deadline < today ? "overdue" : "active")
  const paidPct = principal > 0 ? Math.min(100, (paid / principal) * 100) : 0
  return { principal, paid, remaining, months, monthly, status, paidPct }
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

export interface DebtView {
  debt: Debt
  calc: DebtCalc
  /** Keyingi to'lovgacha kunlar (manfiy — o'tib ketgan); sana yo'q bo'lsa null. */
  daysLeft: number | null
}

/** Ochiq qarzlar yaqin to'lov sanasi bo'yicha, yopilganlari alohida. */
export function splitDebts(debts: readonly Debt[], today: string): { open: DebtView[]; closed: DebtView[] } {
  const views = debts.map((debt) => {
    const due = debt.payDate || debt.deadline
    return { debt, calc: debtCalc(debt, today), daysLeft: due ? daysBetween(today, due) : null }
  })
  const open = views.filter((v) => v.calc.remaining > 0).sort((a, b) => (a.daysLeft ?? 1e9) - (b.daysLeft ?? 1e9))
  const closed = views.filter((v) => v.calc.remaining <= 0)
  return { open, closed }
}
