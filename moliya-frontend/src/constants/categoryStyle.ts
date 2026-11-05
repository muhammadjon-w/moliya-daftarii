// Toifa va moddalarning ko'rinishi: ikonka, rang va "Yangi yozuv" oynasidagi tez tanlov plitkalari.
import type { Group, TxType } from "@/types/ledger"
import type { Tone } from "@/types/ui"
import type { IconName } from "./icons"

export interface Look {
  icon: IconName
  tone: Tone
}

/** Toifa bo'yicha ko'rinish (catalog.ts dagi CATEGORIES kalitlari). */
const CATEGORY_LOOK: Record<string, Look> = {
  housing: { icon: "home", tone: "yellow" },
  telecom: { icon: "phone", tone: "blue" },
  insurance: { icon: "shield", tone: "purple" },
  memberships: { icon: "tag", tone: "purple" },
  subscriptions: { icon: "repeat", tone: "purple" },
  family: { icon: "users", tone: "pink" },
  personal: { icon: "user", tone: "pink" },
  transport: { icon: "bus", tone: "blue" },
  food: { icon: "bowl", tone: "orange" },
  car: { icon: "car", tone: "blue" },
  leisure: { icon: "play", tone: "purple" },
  shopping: { icon: "bag", tone: "pink" },
  marketplaces: { icon: "bag", tone: "pink" },
  education: { icon: "book", tone: "blue" },
  health: { icon: "heart", tone: "red" },
  credits: { icon: "landmark", tone: "red" },
  debts: { icon: "card", tone: "red" },
  cards: { icon: "card", tone: "red" },
  mortgage: { icon: "landmark", tone: "red" },
  arrears: { icon: "card", tone: "red" },
  salary: { icon: "briefcase", tone: "teal" },
  freelance: { icon: "laptop", tone: "teal" },
  business: { icon: "building", tone: "teal" },
  passive: { icon: "trending", tone: "teal" },
  gifts: { icon: "gift", tone: "teal" },
  sales: { icon: "tag", tone: "teal" },
  grant: { icon: "book", tone: "teal" },
  social: { icon: "users", tone: "teal" },
  other_inc: { icon: "plus", tone: "teal" },
}

/** Toifadan farqli ikonka kerak bo'lgan moddalar. */
const ITEM_ICON: Partial<Record<string, IconName>> = {
  internet: "wifi",
  taxi: "car",
  cafe: "coffee",
  clothes: "shirt",
}

const FALLBACK: Record<Group, Look> = {
  inc: { icon: "arrowUp", tone: "teal" },
  pay: { icon: "repeat", tone: "blue" },
  exp: { icon: "bag", tone: "orange" },
  debt: { icon: "card", tone: "red" },
}

export function lookOf(item: string, category: string, group: Group): Look {
  const base = CATEGORY_LOOK[category] ?? FALLBACK[group]
  return { icon: ITEM_ICON[item] ?? base.icon, tone: base.tone }
}

/** Hisobot diagrammasida guruh ranglari. */
export const GROUP_TONE: Record<Group, Tone> = { inc: "teal", pay: "blue", exp: "orange", debt: "red" }

/** "Yangi yozuv" oynasidagi tez tanlov: modda id'lari (catalog.ts ITEMS). Qolganlari "Boshqa" orqali. */
export const QUICK_ITEMS: Record<TxType, readonly string[]> = {
  expense: ["meals", "publictransport", "rent", "mobile", "clothes", "health", "fun"],
  income: ["salary", "bonus", "freelance", "business", "investments", "from_family", "sales"],
}
