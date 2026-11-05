from datetime import datetime

from moliya.accounts.application.ports import AccountRepository, IdentityVerifier
from moliya.accounts.domain.access import Access, access_of
from moliya.accounts.domain.entities import Account
from moliya.shared.domain.errors import SubscriptionRequired


class AuthenticateMiniApp:
    def __init__(self, verifier: IdentityVerifier, accounts: AccountRepository, trial_days: int):
        self._verifier, self._accounts, self._trial_days = verifier, accounts, trial_days

    def execute(self, init_data: str) -> Account | None:
        identity = self._verifier.from_init_data(init_data)
        return self._accounts.upsert_from_identity(identity, self._trial_days) if identity else None


class AuthenticateSite:
    def __init__(self, verifier: IdentityVerifier, accounts: AccountRepository, trial_days: int):
        self._verifier, self._accounts, self._trial_days = verifier, accounts, trial_days

    def execute(self, login_data: dict) -> Account | None:
        identity = self._verifier.from_login_widget(login_data)
        return self._accounts.upsert_from_identity(identity, self._trial_days) if identity else None


def access_for(account: Account, now: datetime) -> Access:
    return access_of(account.trial_ends_at, account.paid_until, now)


def ensure_can_write(account: Account, now: datetime) -> Access:
    access = access_for(account, now)
    if not access.can_write:
        raise SubscriptionRequired("Obuna muddati tugagan.", access=serialize_access(access))
    return access


def serialize_access(access: Access) -> dict:
    return {
        "state": access.state,
        "trialEndsAt": access.trial_ends_at.isoformat(),
        "paidUntil": access.paid_until.isoformat() if access.paid_until else None,
        "daysLeft": access.days_left,
        "canWrite": access.can_write,
    }
