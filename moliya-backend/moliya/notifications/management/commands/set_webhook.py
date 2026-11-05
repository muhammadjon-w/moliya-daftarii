from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from moliya.shared.infrastructure.telegram.bot_client import TelegramBotClient


class Command(BaseCommand):
    help = "Telegram bot webhook'ini ulaydi: python manage.py set_webhook https://api.domen.uz"

    def add_arguments(self, parser):
        parser.add_argument("base_url", help="Backend manzili, masalan https://api.moliyadaftari.uz")

    def handle(self, *args, **options):
        cfg = settings.TELEGRAM
        if not cfg["BOT_TOKEN"] or not cfg["WEBHOOK_SECRET"]:
            raise CommandError(".env faylida BOT_TOKEN va BOT_WEBHOOK_SECRET bo'lishi kerak.")
        url = options["base_url"].rstrip("/") + "/api/v1/telegram/webhook"
        res = TelegramBotClient(cfg["BOT_TOKEN"]).call("setWebhook", {
            "url": url, "secret_token": cfg["WEBHOOK_SECRET"], "allowed_updates": ["message", "my_chat_member"],
        })
        if not res.get("ok"):
            raise CommandError(f"Telegram javobi: {res.get('description')}")
        self.stdout.write(self.style.SUCCESS(f"Webhook ulandi: {url}"))
