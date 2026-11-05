# moliya-backend

Moliya daftari Telegram mini app'i uchun REST API. Django 5 + Django REST Framework + PostgreSQL.

## Arxitektura

Har bir modul to'rt qatlamdan iborat. Bog'liqlik faqat ichkariga qarab yo'naladi: `interfaces → application → domain`, `infrastructure` esa `application`dagi portlarni amalga oshiradi.

```
moliya/
  shared/          umumiy: domen xatolari, vaqt, Telegram imzosi va bot mijozi, UnitOfWork
  accounts/        Telegram foydalanuvchisi, 30 kunlik sinov, obuna holati, autentifikatsiya
  ledger/          tushum/chiqim, qarzlar, oylik reja, sozlamalar, Excel eksport
  billing/         tariflar, buyurtmalar, Payme Merchant API, Click SHOP API, Click hisobi
  notifications/   bot webhook (/start, /obuna, /yordam), eslatmalar
    domain/          sof Python: entity'lar, qoidalar (Django'ni bilmaydi)
    application/     use case'lar va portlar (abstrakt repozitoriylar)
    infrastructure/  Django ORM modellari, repozitoriylar, tashqi xizmatlar
    interfaces/      DRF view'lar, serializer'lar, URL'lar
    container.py     bog'lovchi: portlarni amalga oshirishlar bilan ulaydi
```

## Ishga tushirish (lokal)

```bash
# 1. PostgreSQL (Docker bo'lsa)
docker compose up -d

# 2. Muhit
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # macOS / Linux
pip install -r requirements-dev.txt
copy .env.example .env          # Windows (macOS/Linux: cp)

# 3. Baza va server
python manage.py migrate
python manage.py runserver 8000
```

Tekshirish: http://localhost:8000/health/ → `{"status": "ok"}`

Testlar (PostgreSQL kerak): `pytest`

## Autentifikatsiya

| Kim | Sarlavha |
| --- | --- |
| Mini app | `Authorization: tma <Telegram.WebApp.initData>` |
| To'lov sayti | `X-Telegram-Login: <Login Widget JSON>` |
| Lokal ishlab chiqish | `X-Dev-User-Id: 1001` (faqat `DEBUG=true` va `DEV_AUTH_ENABLED=true`) |

Imzo bot tokeni bilan serverda tekshiriladi; har bir foydalanuvchi faqat o'z yozuvlarini ko'radi.

## API (`/api/v1/`)

| Metod | Manzil | Vazifa |
| --- | --- | --- |
| GET | `me` | foydalanuvchi va obuna holati |
| GET | `ledger/state` | ilova ochilganda kerak bo'lgan hammasi |
| GET, POST | `transactions` | yozuvlar ro'yxati, yangi yozuv |
| PUT, PATCH, DELETE | `transactions/<uuid>` | tahrirlash, o'chirish |
| GET, POST | `debts` | qarzlar |
| PUT, DELETE | `debts/<uuid>` | qarzni tahrirlash, o'chirish |
| POST | `debts/<uuid>/payments` | qarzga to'lov (xohlasa chiqimga ham yoziladi, bitta tranzaksiyada) |
| GET | `plans` | barcha oylar rejasi |
| PUT | `plans/<YYYY-MM>` | oy rejasini saqlash |
| POST | `plans/<YYYY-MM>/copy-previous` | o'tgan oy rejasini ko'chirish |
| GET, PUT | `settings` | dollar kursi, boshlang'ich qoldiq |
| POST | `exports/excel` | Excel hisobotni bot chatiga yuborish |
| GET | `billing/prices` | tariflar (ochiq) |
| GET | `billing/me` | sayt: foydalanuvchi, holat, narxlar |
| POST | `billing/orders` | buyurtma va Payme/Click to'lov havolasi |
| GET | `billing/orders/<id>` | buyurtma holati |
| POST | `billing/invoices` | Click hisobini telefon raqamiga yuborish |
| POST | `payments/payme` | Payme Merchant API endpoint |
| POST | `payments/click` | Click Prepare/Complete endpoint |
| POST | `telegram/webhook` | bot webhook |

Xatolar bitta formatda: `{"error": "<kod>", "message": "<matn>"}`. Obuna tugaganda yozish `402` qaytaradi (o'qish va o'chirish ochiq).

## Telegram va to'lovlar

```bash
python manage.py set_webhook https://api.sizning-domen.uz   # bot webhook'ini ulash
python manage.py send_reminders                              # kuniga bir marta cron orqali
```

- Payme kabinetida Endpoint URL: `https://<api-domen>/api/v1/payments/payme`, hisob maydoni `order_id`.
- Click kabinetida Prepare va Complete URL: `https://<api-domen>/api/v1/payments/click`.

## Production

`DEBUG=false`, `DEV_AUTH_ENABLED=false`, kuchli `SECRET_KEY`, `ALLOWED_HOSTS` va `CORS_ALLOWED_ORIGINS`ni o'z domeningizga sozlang. Ishga tushirish: `gunicorn config.wsgi:application --bind 0.0.0.0:8000`.
