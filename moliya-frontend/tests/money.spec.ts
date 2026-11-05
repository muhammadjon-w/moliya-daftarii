import { describe, expect, it } from "vitest"
import { asciiJson } from "@/rest/client"
import { compact, daysBetween, formatInput, parseMoney, reformatTyping, shortDate } from "@/utils/money"

describe("pul formatlari", () => {
  it("10 000 000 ko'rinishida yozadi va o'qiydi", () => {
    expect(formatInput(10_000_000)).toBe("10 000 000")
    expect(formatInput(1250.5)).toBe("1 250,5")
    expect(formatInput(0)).toBe("")
    expect(parseMoney("10 000 000")).toBe(10_000_000)
    expect(parseMoney("1 250,5")).toBe(1250.5)
    expect(parseMoney("")).toBeNaN()
  })
  it("yozish paytida guruhlaydi", () => {
    expect(reformatTyping("1234567")).toBe("1 234 567")
    expect(reformatTyping("0012.345")).toBe("12,34")
    expect(reformatTyping("-500", true)).toBe("-500")
    expect(reformatTyping("-500")).toBe("500")
  })
  it("qisqa yozuv", () => {
    const uz = { billion: "mlrd", million: "mln", decimal: "," }
    expect(compact(14_250_000, uz)).toBe("14,3 mln")
    expect(compact(-2_500_000_000, uz)).toBe("−2,5 mlrd")
    expect(compact(950_000, uz)).toBe("950\u00a0000")
  })
  it("sanalar", () => {
    expect(shortDate("2026-11-05")).toBe("05.11")
    expect(daysBetween("2026-11-05", "2026-11-15")).toBe(10)
    expect(daysBetween("2026-11-05", "2026-11-01")).toBe(-4)
  })
  it("sarlavha uchun JSON faqat ASCII", () => {
    const s = asciiJson({ first_name: "Мухаммад", id: 1 })
    expect(/^[\x00-\x7f]*$/.test(s)).toBe(true)
    expect(JSON.parse(s).first_name).toBe("Мухаммад")
  })
})
