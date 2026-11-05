"""DRF autentifikatsiya: mini app (initData), sayt (Login Widget), lokal ishlab chiqish rejimi."""
import json

from django.conf import settings
from rest_framework import authentication

from moliya.accounts.application.use_cases import AuthenticateMiniApp, AuthenticateSite
from moliya.accounts.domain.entities import Account
from moliya.accounts.infrastructure.repositories import DjangoAccountRepository, TelegramIdentityVerifier
from moliya.shared.infrastructure.telegram.signatures import TelegramIdentity


class AuthenticatedAccount:
    """request.user sifatida ishlatiladi; ichida domen Account bor."""

    is_authenticated = True
    is_anonymous = False

    def __init__(self, account: Account):
        self.account = account
        self.pk = self.id = account.id

    def __str__(self):
        return f"tg:{self.id}"


class MiniAppAuthentication(authentication.BaseAuthentication):
    """Sarlavha: `Authorization: tma <initData>`."""

    keyword = "tma"

    def authenticate(self, request):
        header = request.headers.get("Authorization", "")
        if not header.lower().startswith(self.keyword + " "):
            return None
        init_data = header[len(self.keyword) + 1:].strip()
        account = AuthenticateMiniApp(TelegramIdentityVerifier(), DjangoAccountRepository(), settings.TRIAL_DAYS).execute(init_data)
        if not account:
            from rest_framework.exceptions import AuthenticationFailed

            raise AuthenticationFailed("Ilovani Telegram ichidan qayta oching.")
        return AuthenticatedAccount(account), None

    def authenticate_header(self, request):
        return self.keyword


class SiteAuthentication(authentication.BaseAuthentication):
    """To'lov sayti: `X-Telegram-Login: <Login Widget JSON>`."""

    def authenticate(self, request):
        raw = request.headers.get("X-Telegram-Login")
        if not raw:
            return None
        try:
            data = json.loads(raw)
        except ValueError:
            data = {}
        account = AuthenticateSite(TelegramIdentityVerifier(), DjangoAccountRepository(), settings.TRIAL_DAYS).execute(data)
        if not account:
            from rest_framework.exceptions import AuthenticationFailed

            raise AuthenticationFailed("Telegram orqali qayta kiring.")
        return AuthenticatedAccount(account), None

    def authenticate_header(self, request):
        return "telegram-login"


class DevAuthentication(authentication.BaseAuthentication):
    """Faqat DEBUG va DEV_AUTH_ENABLED=true bo'lganda: `X-Dev-User-Id: 1001`. Productionda o'chiq."""

    def authenticate(self, request):
        if not settings.DEV_AUTH_ENABLED:
            return None
        raw = request.headers.get("X-Dev-User-Id")
        if not raw or not raw.isdigit():
            return None
        identity = TelegramIdentity(id=int(raw), first_name="Dev", language_code="uz")
        account = DjangoAccountRepository().upsert_from_identity(identity, settings.TRIAL_DAYS)
        return AuthenticatedAccount(account), None
