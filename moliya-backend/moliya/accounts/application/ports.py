from abc import ABC, abstractmethod
from datetime import datetime

from moliya.accounts.domain.entities import Account
from moliya.shared.infrastructure.telegram.signatures import TelegramIdentity


class AccountRepository(ABC):
    @abstractmethod
    def get(self, account_id: int) -> Account | None: ...

    @abstractmethod
    def get_for_update(self, account_id: int) -> Account | None:
        """Tranzaksiya ichida qatorni qulflab o'qiydi."""

    @abstractmethod
    def upsert_from_identity(self, identity: TelegramIdentity, trial_days: int, chat_id: int | None = None) -> Account:
        """Yangi bo'lsa yaratadi (sinov boshlanadi), bo'lsa profilini yangilaydi."""

    @abstractmethod
    def set_paid_until(self, account_id: int, paid_until: datetime | None) -> None: ...

    @abstractmethod
    def set_blocked(self, account_id: int, blocked: bool) -> None: ...

    @abstractmethod
    def set_last_reminder(self, account_id: int, key: str) -> None: ...

    @abstractmethod
    def set_phone(self, account_id: int, phone: str) -> None: ...

    @abstractmethod
    def reminder_candidates(self, now: datetime, horizon_days: int, past_days: int) -> list[Account]: ...


class IdentityVerifier(ABC):
    """Telegram imzosini tekshiradi. Infratuzilma qatlami amalga oshiradi."""

    @abstractmethod
    def from_init_data(self, init_data: str) -> TelegramIdentity | None: ...

    @abstractmethod
    def from_login_widget(self, data: dict) -> TelegramIdentity | None: ...
