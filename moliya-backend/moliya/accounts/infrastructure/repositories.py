from datetime import datetime, timedelta

from django.conf import settings
from django.db.models import Q
from django.utils import timezone

from moliya.accounts.application.ports import AccountRepository, IdentityVerifier
from moliya.accounts.domain.entities import Account
from moliya.accounts.infrastructure.models import AccountModel
from moliya.shared.infrastructure.telegram.signatures import (
    TelegramIdentity,
    validate_init_data,
    validate_login_widget,
)


def _to_entity(m: AccountModel) -> Account:
    return Account(
        id=m.id, first_name=m.first_name, last_name=m.last_name, username=m.username,
        language_code=m.language_code, chat_id=m.chat_id, created_at=m.created_at,
        trial_ends_at=m.trial_ends_at, paid_until=m.paid_until, last_reminder=m.last_reminder,
        blocked_bot=m.blocked_bot, phone=m.phone,
    )


class DjangoAccountRepository(AccountRepository):
    def get(self, account_id: int) -> Account | None:
        m = AccountModel.objects.filter(pk=account_id).first()
        return _to_entity(m) if m else None

    def get_for_update(self, account_id: int) -> Account | None:
        m = AccountModel.objects.select_for_update().filter(pk=account_id).first()
        return _to_entity(m) if m else None

    def upsert_from_identity(self, identity: TelegramIdentity, trial_days: int, chat_id: int | None = None) -> Account:
        profile = {
            "first_name": identity.first_name,
            "last_name": identity.last_name,
            "username": identity.username,
        }
        if identity.language_code:
            profile["language_code"] = identity.language_code
        if chat_id is not None:
            profile["chat_id"] = chat_id
            profile["blocked_bot"] = False
        m, created = AccountModel.objects.get_or_create(
            pk=identity.id,
            defaults={**profile, "trial_ends_at": timezone.now() + timedelta(days=trial_days)},
        )
        if not created:
            changed = [k for k, v in profile.items() if getattr(m, k) != v]
            if changed:
                for k in changed:
                    setattr(m, k, profile[k])
                m.save(update_fields=changed)
        return _to_entity(m)

    def set_paid_until(self, account_id: int, paid_until: datetime | None) -> None:
        AccountModel.objects.filter(pk=account_id).update(paid_until=paid_until)

    def set_blocked(self, account_id: int, blocked: bool) -> None:
        AccountModel.objects.filter(pk=account_id).update(blocked_bot=blocked)

    def set_last_reminder(self, account_id: int, key: str) -> None:
        AccountModel.objects.filter(pk=account_id).update(last_reminder=key)

    def set_phone(self, account_id: int, phone: str) -> None:
        AccountModel.objects.filter(pk=account_id).update(phone=phone)

    def reminder_candidates(self, now: datetime, horizon_days: int, past_days: int) -> list[Account]:
        horizon, past = now + timedelta(days=horizon_days), now - timedelta(days=past_days)
        qs = AccountModel.objects.filter(blocked_bot=False, chat_id__isnull=False).filter(
            Q(trial_ends_at__lte=horizon, trial_ends_at__gte=past) | Q(paid_until__lte=horizon, paid_until__gte=now)
        )[:5000]
        return [_to_entity(m) for m in qs]


class TelegramIdentityVerifier(IdentityVerifier):
    def __init__(self):
        cfg = settings.TELEGRAM
        self._token = cfg["BOT_TOKEN"]
        self._init_age = cfg["INIT_DATA_MAX_AGE"]
        self._login_age = cfg["LOGIN_WIDGET_MAX_AGE"]

    def from_init_data(self, init_data: str) -> TelegramIdentity | None:
        return validate_init_data(init_data, self._token, self._init_age)

    def from_login_widget(self, data: dict) -> TelegramIdentity | None:
        return validate_login_widget(data, self._token, self._login_age)
