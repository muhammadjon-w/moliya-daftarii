# AGENTS.md — Moliya daftari

Telegram mini app: shaxsiy moliya daftari (tushum, chiqim, qarzlar, oylik reja, hisobot) va pullik obuna (Payme / Click).

```
moliya-backend/    Django 5 + DRF + PostgreSQL — REST API va Telegram bot webhook
moliya-frontend/   Vue 3 + TS + TanStack Query — mini app va /obuna to'lov sayti  → batafsil: moliya-frontend/AGENTS.md
render.yaml        Render.com Blueprint: moliya-db, moliya-api, moliya-app
```

## Deploy

- `main` ga push → Render avtomatik deploy qiladi (backend: `moliya-backend/render-start.sh` — migrate, webhook, gunicorn).
- Production: https://moliya-app.onrender.com (mini app), https://moliya-api.onrender.com (API).
- Maxfiy qiymatlar (`BOT_TOKEN` va boshqalar) faqat Render Environment'da. `.env`, `.env.local`, tokenlar git'ga qo'shilmaydi.

## Backend qoidalari (moliya-backend)

```bash
.venv\Scripts\activate
python manage.py runserver 8000
pytest                     # lokal .env da DATABASE_URL=sqlite:///db.sqlite3 bilan ham ishlaydi
```

- Har modul (`accounts`, `ledger`, `billing`, `notifications`) to'rt qatlam: `domain` (sof Python, Django'siz) ← `application` (use case, portlar) ← `infrastructure` (ORM, tashqi xizmatlar) va `interfaces` (DRF view, serializer). Bog'lash — `container.py`.
- Biznes qoidasi `domain/` ga yoziladi va `tests/test_domain.py` da testlanadi. View faqat validatsiya + use case chaqiruvi.
- JSON — camelCase. Xato formati: `{"error": "<kod>", "message": "<matn>"}`. Obuna tugaganda yozish → 402.
- Qarz: `months` — **qolgan** oylar soni. To'liq oylik to'lovda `months − 1` va `payDate + 1 oy` (`Debt.with_payment`).
- Katalog `moliya/ledger/domain/catalog.py` frontend `src/constants/catalog.ts` bilan bir xil bo'lishi shart.
- Telegram `secret_token` faqat `A-Z a-z 0-9 _ -` qabul qiladi — `settings.py` tozalaydi.

## Umumiy

- Kod izohlari va interfeys matnlari o'zbekcha (lotin).
- API shakli o'zgarsa: backend serializer + test → frontend `types/api.ts` + `rest/services` bir commit'da.
