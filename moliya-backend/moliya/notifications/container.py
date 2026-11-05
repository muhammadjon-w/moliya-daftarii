from django.conf import settings

from moliya.accounts.infrastructure.repositories import DjangoAccountRepository
from moliya.notifications.application.use_cases import HandleBotUpdate, SendReminders
from moliya.notifications.infrastructure.bot_gateway import TelegramBotGateway
from moliya.shared.infrastructure.telegram.bot_client import TelegramBotClient


def bot_gateway() -> TelegramBotGateway:
    cfg = settings.TELEGRAM
    return TelegramBotGateway(TelegramBotClient(cfg["BOT_TOKEN"]), cfg["MINI_APP_URL"])


def handle_bot_update() -> HandleBotUpdate:
    return HandleBotUpdate(DjangoAccountRepository(), bot_gateway(), settings.TRIAL_DAYS, settings.TELEGRAM["SITE_URL"])


def send_reminders() -> SendReminders:
    return SendReminders(DjangoAccountRepository(), bot_gateway())
