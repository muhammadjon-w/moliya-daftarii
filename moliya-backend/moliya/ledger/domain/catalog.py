"""Moddalar katalogi (frontend bilan bir xil). Eksport va tekshiruv uchun kerak."""

# toifa -> (uz, ru, en)
CATEGORIES: dict[str, tuple[str, str, str]] = {
    "housing": ("Uy-joy", "Жильё", "Housing"),
    "telecom": ("Aloqa va internet", "Связь и интернет", "Phone & internet"),
    "insurance": ("Sug'urta", "Страхование", "Insurance"),
    "memberships": ("Abonementlar", "Абонементы", "Memberships"),
    "subscriptions": ("Obunalar", "Подписки", "Subscriptions"),
    "family": ("Oila xarajatlari", "Семейные расходы", "Family"),
    "personal": ("Shaxsiy xarajatlar", "Личные расходы", "Personal"),
    "transport": ("Transport", "Транспорт", "Transport"),
    "food": ("Oziq-ovqat va ichimliklar", "Еда и напитки", "Food & drinks"),
    "car": ("Avtomobil", "Автомобиль", "Car"),
    "leisure": ("Ko'ngilochar va dam olish", "Развлечения и отдых", "Leisure & travel"),
    "shopping": ("Xaridlar va buyumlar", "Покупки и вещи", "Shopping"),
    "marketplaces": ("Marketpleyslar", "Маркетплейсы", "Marketplaces"),
    "education": ("Ta'lim va rivojlanish", "Обучение и развитие", "Learning & growth"),
    "health": ("Salomatlik", "Здоровье", "Health"),
    "credits": ("Kreditlar", "Кредиты", "Loans"),
    "debts": ("Qarzlar", "Долги", "Debts"),
    "cards": ("Kredit kartalari", "Кредитные карты", "Credit cards"),
    "mortgage": ("Ipoteka", "Ипотека", "Mortgage"),
    "arrears": ("Qoldiq qarzdorlik", "Остаточная задолженность", "Outstanding debt"),
    "salary": ("Ish haqi (maosh)", "Зарплата", "Salary"),
    "freelance": ("Frilans", "Фриланс", "Freelance"),
    "business": ("Biznes / dividendlar", "Бизнес / дивиденды", "Business / dividends"),
    "passive": ("Passiv daromad", "Пассивный доход", "Passive income"),
    "gifts": ("Sovg'alar va o'tkazmalar", "Подарки и переводы", "Gifts & transfers"),
    "sales": ("Buyumlar sotuvi", "Продажа вещей", "Sale of items"),
    "grant": ("Stipendiya / grant", "Стипендия / грант", "Scholarship / grant"),
    "social": ("Ijtimoiy to'lovlar", "Социальные выплаты", "Social benefits"),
    "other_inc": ("Boshqa tushumlar", "Прочие поступления", "Other income"),
}

# modda -> (toifa, guruh, uz, ru, en)
ITEMS: dict[str, tuple[str, str, str, str, str]] = {
    "rent": ("housing", "pay", "Uy ijarasi", "Аренда жилья", "Home rent"),
    "mobile": ("telecom", "pay", "Mobil aloqa", "Мобильная связь", "Mobile"),
    "internet": ("telecom", "pay", "Internet", "Интернет", "Internet"),
    "insurance": ("insurance", "pay", "Sug'urta", "Страховка", "Insurance"),
    "membership": ("memberships", "pay", "Abonementlar", "Абонементы", "Memberships"),
    "subscription": ("subscriptions", "pay", "Obunalar", "Подписки", "Subscriptions"),
    "utilities": ("housing", "exp", "Kommunal", "Коммуналка", "Utilities"),
    "family": ("family", "exp", "Oila xarajatlari", "Семейные расходы", "Family"),
    "pets": ("family", "exp", "Uy hayvonlari", "Домашние животные", "Pets"),
    "personal": ("personal", "exp", "Shaxsiy", "Личное", "Personal"),
    "selfcare": ("personal", "exp", "O'z-o'ziga parvarish", "Уход за собой", "Self-care"),
    "charity": ("personal", "exp", "Xayriya", "Благотворительность", "Charity"),
    "publictransport": ("transport", "exp", "Transport", "Общественный транспорт", "Public transport"),
    "taxi": ("transport", "exp", "Taksi", "Такси", "Taxi"),
    "meals": ("food", "exp", "Ovqat", "Еда", "Food"),
    "cafe": ("food", "exp", "Kafe va restoranlar", "Кафе и рестораны", "Cafés & restaurants"),
    "car": ("car", "exp", "Avtomobil", "Автомобиль", "Car"),
    "fuel": ("car", "exp", "Benzin", "Бензин", "Fuel"),
    "travel": ("leisure", "exp", "Sayohatlar", "Путешествия", "Travel"),
    "vacation": ("leisure", "exp", "Ta'til", "Отпуск", "Vacation"),
    "fun": ("leisure", "exp", "Ko'ngilochar", "Развлечения", "Entertainment"),
    "alcohol": ("leisure", "exp", "Alkogol", "Алкоголь", "Alcohol"),
    "cigarettes": ("leisure", "exp", "Sigaretlar", "Сигареты", "Cigarettes"),
    "purchases": ("shopping", "exp", "Xaridlar", "Покупки", "Purchases"),
    "clothes": ("shopping", "exp", "Kiyim-kechak", "Одежда", "Clothes"),
    "marketplace": ("marketplaces", "exp", "Marketpleyslar", "Маркетплейсы", "Marketplaces"),
    "education": ("education", "exp", "Ta'lim va rivojlanish", "Обучение", "Education"),
    "hobby": ("education", "exp", "Xobbi", "Хобби", "Hobby"),
    "sport": ("education", "exp", "Sport", "Спорт", "Sport"),
    "health": ("health", "exp", "Salomatlik", "Здоровье", "Health"),
    "credit": ("credits", "debt", "Kreditlar", "Кредиты", "Loans"),
    "debt": ("debts", "debt", "Qarzlar", "Долги", "Debts"),
    "creditcard": ("cards", "debt", "Kredit kartalari", "Кредитные карты", "Credit cards"),
    "mortgage": ("mortgage", "debt", "Ipoteka", "Ипотека", "Mortgage"),
    "arrears": ("arrears", "debt", "Qoldiq qarzdorlik", "Остаточная задолженность", "Outstanding debt"),
    "salary": ("salary", "inc", "Ish haqi", "Зарплата", "Salary"),
    "bonus": ("salary", "inc", "Premiya", "Премия", "Bonus"),
    "freelance": ("freelance", "inc", "Frilans", "Фриланс", "Freelance"),
    "business": ("business", "inc", "Biznes / dividendlar", "Бизнес / дивиденды", "Business / dividends"),
    "investments": ("passive", "inc", "Investitsiyalar va jamg'armalar", "Инвестиции и накопления", "Investments & savings"),
    "realestate": ("passive", "inc", "Ko'chmas mulkdan tushum", "Доход от недвижимости", "Real-estate income"),
    "from_family": ("gifts", "inc", "Oila / do'stlardan o'tkazma", "Переводы от семьи / друзей", "From family / friends"),
    "from_others": ("gifts", "inc", "Uchinchi shaxslardan o'tkazma", "Переводы от третьих лиц", "Third-party transfers"),
    "debt_return": ("gifts", "inc", "Qarz qaytishi", "Возврат долга", "Debt repaid to you"),
    "sales": ("sales", "inc", "Buyumlar sotuvi", "Продажа вещей", "Sale of items"),
    "grant": ("grant", "inc", "Stipendiya / grant", "Стипендия / грант", "Scholarship / grant"),
    "social": ("social", "inc", "Ijtimoiy to'lovlar", "Социальные выплаты", "Social benefits"),
    "other_inc": ("other_inc", "inc", "Boshqa tushumlar", "Прочие поступления", "Other income"),
}

GROUP_LABELS = {
    "inc": ("Tushum", "Поступление", "Income"),
    "pay": ("To'lov", "Платёж", "Payment"),
    "exp": ("Xarajat", "Расход", "Expense"),
    "debt": ("Qarz to'lovi", "Выплата долга", "Debt payment"),
}

_LANG = {"uz": 0, "ru": 1, "en": 2}


def lang_index(lang: str | None) -> int:
    return _LANG.get((lang or "uz")[:2], 0)


def item_label(item: str, lang: str | None = "uz") -> str:
    row = ITEMS.get(item)
    return row[2 + lang_index(lang)] if row else item


def category_label(category: str, lang: str | None = "uz") -> str:
    row = CATEGORIES.get(category)
    return row[lang_index(lang)] if row else category


def group_label(group: str, lang: str | None = "uz") -> str:
    row = GROUP_LABELS.get(group)
    return row[lang_index(lang)] if row else group
