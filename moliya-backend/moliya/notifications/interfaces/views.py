import hmac
import logging

from django.conf import settings
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from moliya.notifications.container import handle_bot_update

log = logging.getLogger(__name__)


class TelegramWebhookView(APIView):
    """POST /api/v1/telegram/webhook — setWebhook'dagi secret_token sarlavha orqali tekshiriladi."""

    authentication_classes: list = []
    permission_classes = [AllowAny]

    def post(self, request):
        secret = settings.TELEGRAM["WEBHOOK_SECRET"]
        given = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if not secret or not hmac.compare_digest(secret, given):
            return Response({"ok": False}, status=403)
        try:
            handle_bot_update().execute(request.data if isinstance(request.data, dict) else {})
        except Exception:  # noqa: BLE001 — Telegram qayta yubormasligi uchun har doim 200
            log.exception("Bot update xatosi")
        return Response({"ok": True})
