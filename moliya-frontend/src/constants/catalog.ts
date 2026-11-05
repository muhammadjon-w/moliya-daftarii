// Moddalar katalogi. Backenddagi moliya/ledger/domain/catalog.py bilan bir xil bo'lishi SHART.
import type { ExpenseGroup, Group } from "@/types/ledger"

/** [uz, ru, en] */
export type Labels = readonly [string, string, string]

export const CATEGORIES: Record<string, Labels> = {
  "housing": ["Uy-joy","Жильё","Housing"],
  "telecom": ["Aloqa va internet","Связь и интернет","Phone & internet"],
  "insurance": ["Sug'urta","Страхование","Insurance"],
  "memberships": ["Abonementlar","Абонементы","Memberships"],
  "subscriptions": ["Obunalar","Подписки","Subscriptions"],
  "family": ["Oila xarajatlari","Семейные расходы","Family"],
  "personal": ["Shaxsiy xarajatlar","Личные расходы","Personal"],
  "transport": ["Transport","Транспорт","Transport"],
  "food": ["Oziq-ovqat va ichimliklar","Еда и напитки","Food & drinks"],
  "car": ["Avtomobil","Автомобиль","Car"],
  "leisure": ["Ko'ngilochar va dam olish","Развлечения и отдых","Leisure & travel"],
  "shopping": ["Xaridlar va buyumlar","Покупки и вещи","Shopping"],
  "marketplaces": ["Marketpleyslar","Маркетплейсы","Marketplaces"],
  "education": ["Ta'lim va rivojlanish","Обучение и развитие","Learning & growth"],
  "health": ["Salomatlik","Здоровье","Health"],
  "credits": ["Kreditlar","Кредиты","Loans"],
  "debts": ["Qarzlar","Долги","Debts"],
  "cards": ["Kredit kartalari","Кредитные карты","Credit cards"],
  "mortgage": ["Ipoteka","Ипотека","Mortgage"],
  "arrears": ["Qoldiq qarzdorlik","Остаточная задолженность","Outstanding debt"],
  "salary": ["Ish haqi (maosh)","Зарплата","Salary"],
  "freelance": ["Frilans","Фриланс","Freelance"],
  "business": ["Biznes / dividendlar","Бизнес / дивиденды","Business / dividends"],
  "passive": ["Passiv daromad","Пассивный доход","Passive income"],
  "gifts": ["Sovg'alar va o'tkazmalar","Подарки и переводы","Gifts & transfers"],
  "sales": ["Buyumlar sotuvi","Продажа вещей","Sale of items"],
  "grant": ["Stipendiya / grant","Стипендия / грант","Scholarship / grant"],
  "social": ["Ijtimoiy to'lovlar","Социальные выплаты","Social benefits"],
  "other_inc": ["Boshqa tushumlar","Прочие поступления","Other income"],
}

export interface CatalogItem {
  id: string
  category: string
  group: Group
  labels: Labels
}

export const ITEMS: readonly CatalogItem[] = [
  { id: "rent", category: "housing", group: "pay", labels: ["Uy ijarasi","Аренда жилья","Home rent"] },
  { id: "mobile", category: "telecom", group: "pay", labels: ["Mobil aloqa","Мобильная связь","Mobile"] },
  { id: "internet", category: "telecom", group: "pay", labels: ["Internet","Интернет","Internet"] },
  { id: "insurance", category: "insurance", group: "pay", labels: ["Sug'urta","Страховка","Insurance"] },
  { id: "membership", category: "memberships", group: "pay", labels: ["Abonementlar","Абонементы","Memberships"] },
  { id: "subscription", category: "subscriptions", group: "pay", labels: ["Obunalar","Подписки","Subscriptions"] },
  { id: "utilities", category: "housing", group: "exp", labels: ["Kommunal","Коммуналка","Utilities"] },
  { id: "family", category: "family", group: "exp", labels: ["Oila xarajatlari","Семейные расходы","Family"] },
  { id: "pets", category: "family", group: "exp", labels: ["Uy hayvonlari","Домашние животные","Pets"] },
  { id: "personal", category: "personal", group: "exp", labels: ["Shaxsiy","Личное","Personal"] },
  { id: "selfcare", category: "personal", group: "exp", labels: ["O'z-o'ziga parvarish","Уход за собой","Self-care"] },
  { id: "charity", category: "personal", group: "exp", labels: ["Xayriya","Благотворительность","Charity"] },
  { id: "publictransport", category: "transport", group: "exp", labels: ["Transport","Общественный транспорт","Public transport"] },
  { id: "taxi", category: "transport", group: "exp", labels: ["Taksi","Такси","Taxi"] },
  { id: "meals", category: "food", group: "exp", labels: ["Ovqat","Еда","Food"] },
  { id: "cafe", category: "food", group: "exp", labels: ["Kafe va restoranlar","Кафе и рестораны","Cafés & restaurants"] },
  { id: "car", category: "car", group: "exp", labels: ["Avtomobil","Автомобиль","Car"] },
  { id: "fuel", category: "car", group: "exp", labels: ["Benzin","Бензин","Fuel"] },
  { id: "travel", category: "leisure", group: "exp", labels: ["Sayohatlar","Путешествия","Travel"] },
  { id: "vacation", category: "leisure", group: "exp", labels: ["Ta'til","Отпуск","Vacation"] },
  { id: "fun", category: "leisure", group: "exp", labels: ["Ko'ngilochar","Развлечения","Entertainment"] },
  { id: "alcohol", category: "leisure", group: "exp", labels: ["Alkogol","Алкоголь","Alcohol"] },
  { id: "cigarettes", category: "leisure", group: "exp", labels: ["Sigaretlar","Сигареты","Cigarettes"] },
  { id: "purchases", category: "shopping", group: "exp", labels: ["Xaridlar","Покупки","Purchases"] },
  { id: "clothes", category: "shopping", group: "exp", labels: ["Kiyim-kechak","Одежда","Clothes"] },
  { id: "marketplace", category: "marketplaces", group: "exp", labels: ["Marketpleyslar","Маркетплейсы","Marketplaces"] },
  { id: "education", category: "education", group: "exp", labels: ["Ta'lim va rivojlanish","Обучение","Education"] },
  { id: "hobby", category: "education", group: "exp", labels: ["Xobbi","Хобби","Hobby"] },
  { id: "sport", category: "education", group: "exp", labels: ["Sport","Спорт","Sport"] },
  { id: "health", category: "health", group: "exp", labels: ["Salomatlik","Здоровье","Health"] },
  { id: "credit", category: "credits", group: "debt", labels: ["Kreditlar","Кредиты","Loans"] },
  { id: "debt", category: "debts", group: "debt", labels: ["Qarzlar","Долги","Debts"] },
  { id: "creditcard", category: "cards", group: "debt", labels: ["Kredit kartalari","Кредитные карты","Credit cards"] },
  { id: "mortgage", category: "mortgage", group: "debt", labels: ["Ipoteka","Ипотека","Mortgage"] },
  { id: "arrears", category: "arrears", group: "debt", labels: ["Qoldiq qarzdorlik","Остаточная задолженность","Outstanding debt"] },
  { id: "salary", category: "salary", group: "inc", labels: ["Ish haqi","Зарплата","Salary"] },
  { id: "bonus", category: "salary", group: "inc", labels: ["Premiya","Премия","Bonus"] },
  { id: "freelance", category: "freelance", group: "inc", labels: ["Frilans","Фриланс","Freelance"] },
  { id: "business", category: "business", group: "inc", labels: ["Biznes / dividendlar","Бизнес / дивиденды","Business / dividends"] },
  { id: "investments", category: "passive", group: "inc", labels: ["Investitsiyalar va jamg'armalar","Инвестиции и накопления","Investments & savings"] },
  { id: "realestate", category: "passive", group: "inc", labels: ["Ko'chmas mulkdan tushum","Доход от недвижимости","Real-estate income"] },
  { id: "from_family", category: "gifts", group: "inc", labels: ["Oila / do'stlardan o'tkazma","Переводы от семьи / друзей","From family / friends"] },
  { id: "from_others", category: "gifts", group: "inc", labels: ["Uchinchi shaxslardan o'tkazma","Переводы от третьих лиц","Third-party transfers"] },
  { id: "debt_return", category: "gifts", group: "inc", labels: ["Qarz qaytishi","Возврат долга","Debt repaid to you"] },
  { id: "sales", category: "sales", group: "inc", labels: ["Buyumlar sotuvi","Продажа вещей","Sale of items"] },
  { id: "grant", category: "grant", group: "inc", labels: ["Stipendiya / grant","Стипендия / грант","Scholarship / grant"] },
  { id: "social", category: "social", group: "inc", labels: ["Ijtimoiy to'lovlar","Социальные выплаты","Social benefits"] },
  { id: "other_inc", category: "other_inc", group: "inc", labels: ["Boshqa tushumlar","Прочие поступления","Other income"] },
]

export const ITEM_BY_ID: Readonly<Record<string, CatalogItem>> = Object.fromEntries(ITEMS.map((i) => [i.id, i]))

export const EXPENSE_GROUPS: readonly ExpenseGroup[] = ["pay", "exp", "debt"]
export const ALL_GROUPS: readonly Group[] = ["inc", ...EXPENSE_GROUPS]
export const METHODS = ["cash", "card", "bank"] as const

/** Guruhga tegishli toifalar, katalogdagi tartibda. */
export function categoriesOfGroup(group: Group): string[] {
  const out: string[] = []
  for (const it of ITEMS) if (it.group === group && !out.includes(it.category)) out.push(it.category)
  return out
}
