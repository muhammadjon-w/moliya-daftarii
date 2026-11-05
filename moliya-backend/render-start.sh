#!/usr/bin/env bash
# Render.com ishga tushirish: migratsiya, bot webhook'i, keyin gunicorn.
set -e

python manage.py migrate --noinput

if [ -n "$BOT_TOKEN" ] && [ -n "$RENDER_EXTERNAL_HOSTNAME" ]; then
  python manage.py set_webhook "https://$RENDER_EXTERNAL_HOSTNAME" || echo "Webhook ulanmadi, keyinroq qayta urinib ko'ring"
fi

exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT:-8000}" --workers 2 --timeout 60
