import { describe, expect, it } from "vitest"
import {
  balanceBefore, cashReport, dailyCumulative, debtBuckets, debtCalc, groupOf, planOverview, planSections, totals, yearRows,
} from "@/domain/ledger"
import type { Debt, Transaction } from "@/domain/types"

let n = 0
const tx = (p: Partial<Transaction>): Transaction => ({
  id: "t" + ++n, type: "expense", group: "exp", item: "meals", category: "food", amount: 0, currency: "UZS",
  date: "2026-11-05", method: "cash", note: "", createdAt: null, ...p,
})
const debt = (p: Partial<Debt>): Debt => ({
  id: "d" + ++n, lender: "Bank", principal: 0, paid: 0, months: 0, status: "", date: null, payDate: null, deadline: null, note: "", createdAt: null, ...p,
})
const RATE = 12_000

describe("totals", () => {
  it("guruhlar bo'yicha yig'adi va dollarni so'mga aylantiradi", () => {
    const list = [
      tx({ type: "income", group: "inc", item: "salary", category: "salary", amount: 10_000_000 }),
      tx({ type: "income", group: "inc", amount: 100, currency: "USD" }),
      tx({ group: "pay", amount: 2_000_000 }),
      tx({ group: "exp", amount: 500_000 }),
      tx({ group: "debt", amount: 1_000_000 }),
    ]
    const t = totals(list, RATE)
    expect(t.inc).toBe(11_200_000)
    expect(t.out).toBe(3_500_000)
    expect(t.net).toBe(7_700_000)
    expect(t.incUsd).toBe(100)
  })

  it("noma'lum guruh chiqim sifatida hisoblanadi", () => {
    expect(groupOf({ type: "expense", group: "inc" })).toBe("exp")
    expect(groupOf({ type: "income", group: "pay" })).toBe("inc")
  })
})

describe("balanceBefore va yearRows", () => {
  const all = [
    tx({ type: "income", group: "inc", amount: 5_000_000, date: "2026-01-10" }),
    tx({ amount: 1_000_000, date: "2026-01-20" }),
    tx({ amount: 500_000, date: "2026-02-01" }),
    tx({ type: "income", group: "inc", amount: 1_000_000, date: "2025-12-31" }),
  ]
  it("oy boshidagi qoldiqqa boshlang'ich summa va oldingi oylar kiradi", () => {
    expect(balanceBefore(all, 2026, 0, RATE, 200_000)).toBe(1_200_000)
    expect(balanceBefore(all, 2026, 1, RATE, 200_000)).toBe(5_200_000)
  })
  it("yil jadvali oy oxiridagi qoldiqni yig'ib boradi", () => {
    const rows = yearRows(all, 2026, RATE, 0)
    expect(rows).toHaveLength(12)
    expect(rows[0].end).toBe(5_000_000)
    expect(rows[1].end).toBe(4_500_000)
    expect(rows[11].end).toBe(4_500_000)
  })
})

describe("dailyCumulative", () => {
  it("o'tgan oyda oxirgi kungacha yig'iladi", () => {
    const arr = dailyCumulative([tx({ amount: 100, date: "2026-02-03" }), tx({ amount: 50, date: "2026-02-10" })], 2026, 1, RATE, () => true, new Date(2026, 5, 1))
    expect(arr).toHaveLength(28)
    expect(arr[1]).toBe(0)
    expect(arr[2]).toBe(100)
    expect(arr[27]).toBe(150)
  })
})

describe("qarzlar", () => {
  it("qoldiq, oylik to'lov va holatni hisoblaydi", () => {
    const c = debtCalc({ principal: 12_000_000, paid: 2_000_000, months: 10 }, "2026-11-05")
    expect(c.remaining).toBe(10_000_000)
    expect(c.monthly).toBe(1_000_000)
    expect(c.status).toBe("active")
    expect(debtCalc({ principal: 100, paid: 100, months: 0 }, "2026-11-05").status).toBe("paid")
    expect(debtCalc({ principal: 100, paid: 0, months: 0, deadline: "2026-01-01" }, "2026-11-05").status).toBe("overdue")
  })
  it("muddatlar bo'yicha guruhlaydi", () => {
    const b = debtBuckets(
      [
        debt({ principal: 100, payDate: "2026-11-01" }),
        debt({ principal: 200, payDate: "2026-11-20" }),
        debt({ principal: 300, deadline: "2026-12-25" }),
        debt({ principal: 400 }),
        debt({ principal: 500, paid: 500 }),
      ],
      "2026-11-05",
    )
    expect(b).toEqual({ overdue: 100, d30: 200, d60: 300, later: 400, total: 1000 })
  })
})

describe("reja", () => {
  const list = [tx({ group: "exp", category: "food", amount: 900_000 }), tx({ type: "income", group: "inc", category: "salary", amount: 8_000_000 })]
  const plan = { "exp:food": 600_000, "inc:salary": 10_000_000 }
  it("bo'limlar fakt va farqni beradi", () => {
    const s = planSections(list, plan, RATE)
    const inc = s.find((x) => x.group === "inc")!
    const exp = s.find((x) => x.group === "exp")!
    expect(inc.diff).toBe(-2_000_000)
    expect(exp.rows.find((r) => r.category === "food")!.diff).toBe(-300_000)
  })
  it("oshib ketgan toifalarni topadi", () => {
    expect(planOverview(list, plan, RATE)).toEqual({ income: 10_000_000, outflow: 600_000, overruns: [{ category: "food", over: 300_000 }] })
  })
})

describe("kassa", () => {
  it("usullar bo'yicha boshlang'ich, kirim, chiqim va qoldiq", () => {
    const r = cashReport(
      [
        tx({ type: "income", group: "inc", amount: 1000, method: "card", date: "2026-10-01" }),
        tx({ type: "income", group: "inc", amount: 500, method: "card", date: "2026-11-02" }),
        tx({ amount: 200, method: "card", date: "2026-11-03" }),
        tx({ amount: 10, currency: "USD", date: "2026-11-03" }),
      ],
      2026,
      10,
    )
    expect(r.byMethod.find((x) => x.method === "card")!.row).toEqual({ start: 1000, inflow: 500, outflow: 200, end: 1300 })
    expect(r.total.end).toBe(1300)
    expect(r.usd).toEqual({ start: 0, inflow: 0, outflow: 10, end: -10 })
  })
})
