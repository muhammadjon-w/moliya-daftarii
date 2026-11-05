# AGENTS.md — moliya-frontend

Telegram mini app "Moliya daftari" interfeysi. Vue 3 (`<script setup>`) + TypeScript (strict) + TanStack Query + Vite.
Bu fayl kod yozuvchi agentlar va dasturchilar uchun: qayerga nima yoziladi va qanday qoidalar bor.

## Buyruqlar

```bash
npm run dev         # http://localhost:5173 (backend 8000-portda bo'lishi kerak, /api proxy orqali)
npm run typecheck   # vue-tsc — har o'zgarishdan keyin
npm run test        # vitest (tests/*.spec.ts)
npm run build       # typecheck + production build (dist/)
```

O'zgarish tugadi deyishdan oldin `typecheck` va `test` o'tishi shart.

## Papkalar

```
src/
  pages/        sahifalar (har biri bitta route)
  features/     sahifa bo'laklari, bo'lim bo'yicha: home/ records/ report/ debts/ plan/ paywall/ settings/ subscribe/ shell/
  components/   bir nechta sahifada ishlatiladigan UI
  composables/  qayta ishlatiladigan reaktiv mantiq (use*)
  rest/         server bilan aloqa
    client.ts     fetch qatlami, ApiError, auth sarlavhalari
    services/     faqat HTTP chaqiruvlar (*.service.ts)
    queries/      TanStack Query: so'rovlar (*.queries.ts) va mutatsiyalar (*.mutations.ts)
  plugins/      ilovaga ulanadigan narsalar: router, vueQuery, telegram SDK, i18n (uz/ru/en lug'atlari)
  types/        TypeScript tiplari (ledger, account, api, ui)
  constants/    o'zgarmas qiymatlar: katalog, ikonkalar, ranglar, query kalitlari, route nomlari, ENV
  utils/        sof funksiyalar: pul/sana formatlari, hisob-kitob (Vue'siz, testlanadi)
  styles/       tokens.css (dizayn tokenlari) va base.css (global stillar)
  App.vue, main.ts
tests/          utils/ uchun unit testlar
```

## Bog'liqlik yo'nalishi

```
pages → features → components
  ↓        ↓           ↓
      composables → rest/queries → rest/services → rest/client
                 ↘      ↓
                  utils, constants, types   (hech narsani import qilmaydi, faqat bir-birini)
```

Qoidalar:

1. **pages** faqat sahifani yig'adi: `features/` va `components/` dan bo'laklar oladi, `composables/` dan ma'lumot oladi. Uzun shablon, murakkab hisob yoki katta stil sahifada bo'lmaydi — ular `features/<bo'lim>/` ga chiqariladi.
2. **features/<bo'lim>/** — shu bo'limning komponentlari. Bir feature boshqa bo'limning feature'ini import qilmaydi. Ikki sahifaga kerak bo'lib qolsa → `components/` ga ko'chiriladi (masalan `TransactionRow`, `PlanOptions`).
3. **components/** — sahifani bilmaydigan UI. Ma'lumotni props orqali oladi, `rest/` ni chaqirmaydi. `useI18n`, `useUi` kabi composable ishlatishi mumkin.
4. **composables/** — `use*` funksiyalar. Komponentlar Telegram, til, oy, oynalar bilan shu yerdagi composable orqali ishlaydi (`useTelegram`, `useI18n`, `useMonth`, `useSheets`, `useUi`).
5. **rest/services/** — faqat `api.get/post/...` chaqiruvi, kesh va holat yo'q. Komponent service'ni to'g'ridan-to'g'ri chaqirmaydi.
6. **rest/queries/** — komponentlar server ma'lumotini faqat shu hook'lar orqali oladi va o'zgartiradi.
7. **utils/** — sof funksiyalar: Vue, DOM, fetch yo'q. Har yangi hisob-kitob funksiyasiga `tests/` da test yoziladi.
8. **constants/** va **types/** hech qanday ilova kodini import qilmaydi (bir-birini mumkin).
9. `import.meta.env` faqat `constants/app.ts` da o'qiladi (`ENV`). Telegram SDK (`window.Telegram`) faqat `plugins/telegram.ts` da.

Import har doim `@/` alias bilan (`@/utils/money`), bir papka ichida esa `./Fayl.vue`.

## Ma'lumot oqimi (TanStack Query)

- Ilova ochilganda bitta so'rov: `GET ledger/state` (`useLedgerQuery`). Sahifalardagi barcha raqamlar shu keshdan `utils/ledger.ts` funksiyalari bilan hisoblanadi — har sahifa uchun alohida endpoint qo'shilmaydi.
- Query kalitlari faqat `constants/queryKeys.ts` dan. Qo'lda `["ledger", ...]` yozilmaydi.
- Yozish — `rest/queries/*.mutations.ts` dagi hook'lar. Ular **optimistik**: `onMutate` keshni darhol o'zgartiradi, `onError` orqaga qaytaradi, `onSuccess` server javobini yozadi. Yangi mutatsiya ham shu `cache()` yordamchisi bilan yoziladi.
- Server hisoblaydigan narsa (qarz to'lovi: qoldiq, keyingi sana) optimistik qilinmaydi — `onSuccess` kutiladi.
- Xatolar bir joyda: `plugins/vueQuery.ts`. 402 → to'lov oynasi, boshqasi → toast. Komponentda `onError` faqat maxsus holat uchun.
- Server ma'lumoti `useUi` ga yoki `ref` ga nusxalanmaydi. `useUi` faqat interfeys holati: tanlangan oy, til, toast, ochiq oyna.

## Oynalar (bottom sheet)

- Bir vaqtda bitta oyna: `useUi().ui.sheet` (`types/ui.ts` dagi `Sheet` turi). Ochish — `useSheets()` orqali (`newRecord`, `editDebt`, `payDebt`, ...): u obuna tugaganini tekshiradi va kerak bo'lsa to'lov oynasini ochadi.
- Oynalar `features/shell/AppShell.vue` da chiziladi. Yangi oyna: `Sheet` turiga variant qo'shing → `features/<bo'lim>/XSheet.vue` (ichida `BaseSheet`) → `AppShell` ga qator → `useSheets` ga ochuvchi funksiya.
- `/obuna` (to'lov sayti) — `meta.standalone`: AppShell yuklanmaydi, ledger so'rovi yuborilmaydi.

## Matnlar (i18n)

- Interfeysdagi har bir matn `plugins/i18n/uz.ts` dagi kalit orqali: `t("key")`. Shablonga o'zbekcha matn qo'lda yozilmaydi.
- Yangi kalit avval `uz.ts` ga, keyin `ru.ts` va `en.ts` ga — TypeScript to'liqligini tekshiradi (kalit yetishmasa typecheck yiqiladi).
- O'zgaruvchilar: `t("debt_paid", { v: num(x) })` → `"To'langan {v}"`.
- Pul: `num()` / `sum()` / `compact()` / `signedAmount()` (`useI18n` yoki `utils/money`). `toLocaleString` ni komponentda chaqirmang.

## Katalog

- `constants/catalog.ts` (moddalar va toifalar) backenddagi `moliya/ledger/domain/catalog.py` bilan **bir xil bo'lishi shart**. Biri o'zgarsa — ikkinchisi ham.
- Ikonka va rang: `constants/categoryStyle.ts` (`lookOf`), "Yangi yozuv" plitkalari: `QUICK_ITEMS`.

## Dizayn va stil

- Maket: navy fon, teal aksent, katta yumaloq kartochkalar (Jost shrifti). Ranglar, radiuslar, soyalar — `styles/tokens.css`. Komponentda `#hex` yozilmaydi: `var(--teal)`, `rgba(var(--tone-red), 0.14)`.
- Rangli plitka/ikonka uchun `Tone` (`teal | red | yellow | blue | orange | purple | pink`) va `--tone-*` o'zgaruvchilari.
- Komponent stili — `<style scoped>`, BEM'ga yaqin nomlar (`.dc__head`, `.pill--red`). Umumiy klasslar (`.page`, `.card`, `.btn`, `.input`, `.field`, `.section-title`) — `styles/base.css`.
- Ikonkalar — `<AppIcon name="..." />`, yangisi `constants/icons.ts` ga (24×24 path). Tashqi ikonka kutubxonasi qo'shilmaydi.
- Mobil birinchi: 360–430px kenglikda tekshiring, gorizontal scroll bo'lmasin. Pastki navigatsiya uchun `.page` pastdan joy qoldiradi.

## Vue uslubi

- Faqat `<script setup lang="ts">`. Props/emits — `defineProps<...>()`, `defineEmits<...>()`, ikki tomonlama bog'lash — `defineModel`.
- Har fayl boshida bir qatorli izoh: komponent nima qiladi (o'zbekcha).
- `any` ishlatilmaydi. Server javobi tiplari — `types/api.ts`.
- Kirish maydonlari: pul uchun `MoneyInput`, tanlov uchun `SegmentedControl`.

## Telegram

- `plugins/telegram.ts`: `initData` har so'rovda `Authorization: tma ...` sarlavhasida ketadi (`rest/client.ts`). Imzoni server tekshiradi.
- Lokal: Telegram'siz brauzerda `VITE_DEV_USER_ID` bilan (`.env.local`), backendda `DEBUG=true` va `DEV_AUTH_ENABLED=true` bo'lishi kerak.
- To'lov Telegram ichida emas: to'lov oynasi `ENV.siteUrl/obuna?months=..&provider=..` ni tashqi brauzerda ochadi.
- Bepul serverda backend uxlab qoladi: birinchi so'rov 50+ soniya. `REQUEST_TIMEOUT_MS` va `QueryState` dagi "server uyg'onmoqda" xabari shu uchun.

## Yangi narsa qo'shish — tez yo'riqnoma

| Nima | Qayerga |
| --- | --- |
| Yangi sahifa | `pages/XPage.vue` + `constants/routes.ts` + `plugins/router.ts` |
| Sahifa bo'lagi | `features/<bo'lim>/X.vue` |
| Bir necha sahifaga umumiy UI | `components/X.vue` |
| Yangi endpoint | `rest/services/*.service.ts` → `rest/queries/*` → `types/api.ts` |
| Hisob-kitob | `utils/ledger.ts` + `tests/ledger.spec.ts` |
| Matn | `plugins/i18n/uz.ts`, `ru.ts`, `en.ts` |
| Rang / o'lcham | `styles/tokens.css` |
