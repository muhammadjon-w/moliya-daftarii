import { describe, expect, it } from "vitest"
import type { Debt, Transaction } from "@/types/ledger"
import {
  balanceBefore, changePct, debtCalc, debtSummary, expenseShares, groupOf, percent, plannedRows, planRows, planStatus,
  sortNewestFirst, splitDebts, topItems, totals,
} from "@/utils/ledger"

let n = 0
const tx = (p: Partial<Transaction>): Transaction => ({
  id: "t" + ++n, type: "expense", group: "exp", item: "meals", category: "food", amount: 0, currency: "UZS",
  date: "2026-11-05", method: "cash", note: "", createdAt: null, ...p,
})
const debt = (p: Partial<Debt>): Debt => ({
  id: "d" + ++n, lender: "Bank", principal: 0, paid: 0, months: 0, status: "", date: null, payDate: null, deadline: null, note: "", createdAt: null, ...p,
})
const RATE = 12_000
const income = (p: Partial<Transaction>) => tx({ type: "income", group: "inc", item: "salary", category: "salary", ...p })

describe("totals", () => {
  it("guruhlar bo'yicha yig'adi va dollarni so'mga aylantiradi", () => {
    const t = totals(
      [income({ amount: 10_000_000 }), income({ amount: 100, currency: "USD" }), tx({ group: "pay", amount: 2_000_000 }), tx({ amount: 500_000 }), tx({ group: "debt", amount: 1_000_000 })],
      RATE,
    )
    expect(t.inc).toBe(11_200_000)
    expect(t.out).toBe(3_500_000)
    expect(t.net).toBe(7_700_000)
  })

  it("noma'lum guruh chiqim sifatida hisoblanadi", () => {
    expect(groupOf({ type: "expense", group: "inc" })).toBe("exp")
    expect(groupOf({ type: "income", group: "pay" })).toBe("inc")
  })

  it("oy boshidagi qoldiqqa boshlang'ich summa va oldingi oylar kiradi", () => {
    const all = [income({ amount: 5_000_000, date: "2026-01-10" }), tx({ amount: 1_000_000, date: "2026-01-20" }), income({ amount: 1_000_000, date: "2025-12-31" })]
    expect(balanceBefore(all, 2026, 0, RATE, 200_000)).toBe(1_200_000)
    expect(balanceBefore(all, 2026, 1, RATE, 200_000)).toBe(5_200_000)
  })

  it("foizlar", () => {
    expect(percent(10_250_000, 28_400_000)).toBe(36)
    expect(percent(1, 0)).toBeNull()
    expect(changePct(28_400_000, 14_000_000)).toBe(103)
    expect(changePct(5, 0)).toBeNull()
  })

  it("yangi yozuvlar birinchi", () => {
    const a = tx({ date: "2026-11-03" })
    const b = tx({ date: "2026-11-05", createdAt: "2026-11-05T08:00:00Z" })
    const c = tx({ date: "2026-11-05", createdAt: "2026-11-05T09:00:00Z" })
    expect(sortNewestFirst([a, b, c]).map((x) => x.id)).toEqual([c.id, b.id, a.id])
  })
})

describe("hisobot", () => {
  it("chiqim ulushlari yig'indisi 100%", () => {
    const s = expenseShares(totals([tx({ group: "pay", amount: 4_500_000 }), tx({ amount: 3_500_000 }), tx({ group: "debt", amount: 2_000_000 }), tx({ amount: 250_000 })], RATE))
    expect(s.map((x) => x.group)).toEqual(["pay", "exp", "debt"])
    expect(s.reduce((a, x) => a + x.pct, 0)).toBe(100)
    expect(expenseShares(totals([], RATE))).toEqual([])
  })

  it("eng ko'p sarflangan moddalar", () => {
    const top = topItems([tx({ item: "rent", category: "housing", group: "pay", amount: 4_500_000 }), tx({ item: "meals", amount: 1_000_000 }), tx({ item: "meals", amount: 1_600_000 }), income({ amount: 9e9 })], RATE, false)
    expect(top.map((x) => [x.item, x.value])).toEqual([["rent", 4_500_000], ["meals", 2_600_000]])
  })
})

describe("reja", () => {
  const list = [tx({ category: "food", amount: 2_600_000 }), income({ amount: 14_000_000 })]
  const plan = { "exp:food": 2_000_000, "inc:salary": 15_000_000, "exp:transport": 500_000 }

  it("toifa bo'yicha reja va fakt", () => {
    const food = planRows(list, plan, RATE, "exp").find((r) => r.category === "food")!
    expect([food.plan, food.fact]).toEqual([2_000_000, 2_600_000])
  })

  it("holat: oshdi / qoldi / foiz", () => {
    expect(planStatus({ group: "exp", plan: 2_000_000, fact: 2_600_000 })).toEqual({ kind: "over", amount: 600_000 })
    expect(planStatus({ group: "exp", plan: 500_000, fact: 0 })).toEqual({ kind: "left", amount: 500_000 })
    expect(planStatus({ group: "inc", plan: 15_000_000, fact: 14_000_000 })).toEqual({ kind: "progress", pct: 93 })
    expect(planStatus({ group: "inc", plan: 1, fact: 2 })).toEqual({ kind: "done" })
  })

  it("rejali qatorlar: oshib ketganlar birinchi", () => {
    expect(plannedRows(list, plan, RATE).map((r) => r.category)).toEqual(["food", "salary", "transport"])
  })
})

describe("qarzlar", () => {
  it("qoldiq, oylik to'lov va holat", () => {
    const c = debtCalc({ principal: 24_000_000, paid: 6_000_000, months: 12 }, "2026-11-05")
    expect([c.remaining, c.monthly, c.status, c.paidPct]).toEqual([18_000_000, 1_500_000, "active", 25])
    expect(debtCalc({ principal: 100, paid: 100, months: 0 }, "2026-11-05").status).toBe("paid")
    expect(debtCalc({ principal: 100, paid: 0, months: 0, deadline: "2026-01-01" }, "2026-11-05").status).toBe("overdue")
  })

  it("jami va faol qarzlar", () => {
    const s = debtSummary([debt({ principal: 24_000_000, paid: 6_000_000, months: 12 }), debt({ principal: 5_000_000, paid: 1_000_000, months: 4 }), debt({ principal: 10, paid: 10 })], "2026-11-05")
    expect(s).toEqual({ principal: 29_000_010, paid: 7_000_010, remaining: 22_000_000, monthly: 2_500_000, openCount: 2 })
  })

  it("yaqin to'lov bo'yicha tartib, yopilganlari alohida", () => {
    const later = debt({ principal: 100, payDate: "2026-12-01" })
    const soon = debt({ principal: 100, payDate: "2026-11-15" })
    const noDate = debt({ principal: 100 })
    const closed = debt({ principal: 100, paid: 100 })
    const { open, closed: done } = splitDebts([later, noDate, closed, soon], "2026-11-05")
    expect(open.map((v) => [v.debt.id, v.daysLeft])).toEqual([[soon.id, 10], [later.id, 26], [noDate.id, null]])
    expect(done.map((v) => v.debt.id)).toEqual([closed.id])
  })
})
