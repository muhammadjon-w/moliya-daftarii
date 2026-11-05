# moliya-frontend

Moliya daftari Telegram mini app'ining interfeysi. Vue 3 + TypeScript + TanStack Query + Pinia + Vite.
Dizayn: to'q ko'k (navy) fon va "Liquid Glass" effekti. Bo'limlar: Bosh sahifa, Daromadlar, Chiqimlar, Reja va fakt, Yil, Qarzlar, Hisobot. To'lov sahifasi: `/obuna`.

## Arxitektura

Bog'liqlik faqat ichkariga yo'naladi: `presentation → application → domain`. `infrastructure` application'dagi portlarni amalga oshiradi, `app/container.ts` ularni ulaydi.

```
src/
  domain/          sof TypeScript: tiplar, katalog (48 modda), pul formatlari, hisob-kitob (oylik, yil, qarz, reja, kassa)
  application/     portlar (LedgerGateway, BillingGateway, Platform), TanStack Query so'rovlari va mutatsiyalari,
                   Pinia store (tanlangan oy, til, bildirishnoma), useMonth — tanlangan oy ko'rsatkichlari
  infrastructure/  fetch mijozi (ApiError), Telegram WebApp adapteri, HTTP gateway'lar
  presentation/    Vue komponentlari, sahifalar, i18n (uz/ru/en), uslublar
  app/             App.vue, router, kompozitsiya ildizi (container.ts)
tests/             domen qatlami testlari (vitest)
```

Ma'lumot oqimi: ilova ochilganda bitta so'rov `GET ledger/state` — keyin barcha sahifalar shu keshdan hisoblanadi.
Yozishlar optimistik: yozuv darhol ko'rinadi, server xato qaytarsa orqaga qaytariladi. Obuna tugaganda (402) to'lov oynasi chiqadi.

## Ishga tushirish (lokal)

Node.js 20+ kerak. Avval `moliya-backend`ni ishga tushiring (8000-port).

```bash
npm install
copy .env.example .env.local     # Windows (macOS/Linux: cp)
npm run dev                      # http://localhost:5173
```

Lokal rejimda Telegram'siz brauzerda ochiladi: `VITE_DEV_USER_ID` foydalanuvchisi bo'lib kiriladi (backend'da `DEBUG=true`, `DEV_AUTH_ENABLED=true` bo'lishi shart). `/api` so'rovlari Vite proxy orqali Django'ga boradi.

Tekshirish:

```bash
npm run test        # domen testlari
npm run typecheck   # TypeScript
npm run build       # dist/ — serverga yuklanadigan statik fayllar
```

## Telegram mini app sifatida

1. `.env.production` yarating: `VITE_API_BASE_URL=https://api.<domen>/api/v1`, `VITE_BOT_USERNAME=<bot nomi>`, `VITE_SITE_URL=https://app.<domen>`. `VITE_DEV_USER_ID`ni yozmang.
2. `npm run build`, `dist/` papkasini HTTPS'li domenga joylang. Barcha manzillar `index.html`ga qaytishi kerak (nginx: `try_files $uri /index.html;`).
3. @BotFather → botingiz → Bot Settings → Menu Button / Configure Mini App → shu domen.
4. To'lov sahifasidagi Telegram Login uchun: @BotFather → `/setdomain` → shu domen.
5. Backend `.env`: `MINI_APP_URL` va `SITE_URL` shu domen, `CORS_ALLOWED_ORIGINS` ham shu domen.

Mini app ichida so'rovlar `Authorization: tma <initData>` sarlavhasi bilan yuboriladi, imzoni server bot tokeni bilan tekshiradi. To'lov Telegram ichida emas, `/obuna` sahifasida (oddiy brauzerda) amalga oshiriladi.
