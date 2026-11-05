"""Django sozlamalari. Barcha maxfiy va muhitga bog'liq qiymatlar .env faylidan o'qiladi."""
import re
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    DEV_AUTH_ENABLED=(bool, False),
    ALLOWED_HOSTS=(list, ["localhost", "127.0.0.1"]),
    CORS_ALLOWED_ORIGINS=(list, ["http://localhost:5173", "http://127.0.0.1:5173"]),
    CSRF_TRUSTED_ORIGINS=(list, []),
    TRIAL_DAYS=(int, 30),
    INIT_DATA_MAX_AGE=(int, 86400),
    LOGIN_WIDGET_MAX_AGE=(int, 7 * 86400),
)
environ.Env.read_env(BASE_DIR / ".env")

SECRET_KEY = env("SECRET_KEY", default="dev-only-change-me")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env("ALLOWED_HOSTS")
CSRF_TRUSTED_ORIGINS = env("CSRF_TRUSTED_ORIGINS")

# Render.com: xizmatning o'z manzili va frontend (static site) manzili avtomatik beriladi.
RENDER_EXTERNAL_HOSTNAME = env("RENDER_EXTERNAL_HOSTNAME", default="")
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)
FRONTEND_HOST = env("FRONTEND_HOST", default="")
FRONTEND_ORIGIN = f"https://{FRONTEND_HOST}" if FRONTEND_HOST else ""

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.staticfiles",
    "rest_framework",
    "corsheaders",
    "moliya.accounts",
    "moliya.ledger",
    "moliya.billing",
    "moliya.notifications",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    }
]

DATABASES = {
    "default": env.db("DATABASE_URL", default="postgres://moliya:moliya@localhost:5432/moliya"),
}
DATABASES["default"]["ATOMIC_REQUESTS"] = False
DATABASES["default"]["CONN_MAX_AGE"] = env.int("DB_CONN_MAX_AGE", default=60)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LANGUAGE_CODE = "uz"
TIME_ZONE = "Asia/Tashkent"
USE_I18N = False
USE_TZ = True
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS")
if FRONTEND_ORIGIN:
    CORS_ALLOWED_ORIGINS.append(FRONTEND_ORIGIN)
    CSRF_TRUSTED_ORIGINS.append(FRONTEND_ORIGIN)
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "x-telegram-login",
    "x-dev-user-id",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "moliya.accounts.interfaces.authentication.MiniAppAuthentication",
        "moliya.accounts.interfaces.authentication.DevAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["moliya.accounts.interfaces.permissions.IsTelegramAccount"],
    "DEFAULT_RENDERER_CLASSES": ["rest_framework.renderers.JSONRenderer"],
    "DEFAULT_PARSER_CLASSES": ["rest_framework.parsers.JSONParser"],
    "EXCEPTION_HANDLER": "moliya.shared.interfaces_exception_handler.exception_handler",
    "UNAUTHENTICATED_USER": None,
}

# --- Ilova sozlamalari ---
TELEGRAM = {
    "BOT_TOKEN": env("BOT_TOKEN", default=""),
    "BOT_USERNAME": env("BOT_USERNAME", default=""),
    # Telegram secret_token faqat A-Z a-z 0-9 _ - qabul qiladi (Render generateValue'da + / = bo'ladi).
    "WEBHOOK_SECRET": re.sub(r"[^A-Za-z0-9_-]", "", env("BOT_WEBHOOK_SECRET", default=""))[:256],
    "MINI_APP_URL": env("MINI_APP_URL", default=f"{FRONTEND_ORIGIN}/" if FRONTEND_ORIGIN else ""),
    "SITE_URL": env("SITE_URL", default=FRONTEND_ORIGIN),
    "INIT_DATA_MAX_AGE": env("INIT_DATA_MAX_AGE"),
    "LOGIN_WIDGET_MAX_AGE": env("LOGIN_WIDGET_MAX_AGE"),
}
TRIAL_DAYS = env("TRIAL_DAYS")
PRICES_JSON = env("PRICES_JSON", default='{"1": 29000, "6": 149000, "12": 249000}')
# Faqat lokal ishlab chiqish uchun: X-Dev-User-Id sarlavhasi bilan Telegram'siz kirish.
DEV_AUTH_ENABLED = DEBUG and env("DEV_AUTH_ENABLED")

PAYME = {
    "MERCHANT_ID": env("PAYME_MERCHANT_ID", default=""),
    "KEY": env("PAYME_KEY", default=""),
    "CHECKOUT_URL": env("PAYME_CHECKOUT_URL", default="https://checkout.paycom.uz"),
}
CLICK = {
    "SERVICE_ID": env("CLICK_SERVICE_ID", default=""),
    "MERCHANT_ID": env("CLICK_MERCHANT_ID", default=""),
    "MERCHANT_USER_ID": env("CLICK_MERCHANT_USER_ID", default=""),
    "SECRET_KEY": env("CLICK_SECRET_KEY", default=""),
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_CONTENT_TYPE_NOSNIFF = True
