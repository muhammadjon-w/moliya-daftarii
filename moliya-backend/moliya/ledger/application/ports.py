from abc import ABC, abstractmethod
from uuid import UUID

from moliya.ledger.domain.entities import Debt, LedgerSettings, MonthPlan, Transaction


class TransactionRepository(ABC):
    @abstractmethod
    def list(self, account_id: int) -> list[Transaction]: ...

    @abstractmethod
    def get(self, account_id: int, tx_id: UUID) -> Transaction | None: ...

    @abstractmethod
    def add(self, tx: Transaction) -> Transaction: ...

    @abstractmethod
    def update(self, tx: Transaction) -> Transaction: ...

    @abstractmethod
    def delete(self, account_id: int, tx_id: UUID) -> bool: ...


class DebtRepository(ABC):
    @abstractmethod
    def list(self, account_id: int) -> list[Debt]: ...

    @abstractmethod
    def get(self, account_id: int, debt_id: UUID, for_update: bool = False) -> Debt | None: ...

    @abstractmethod
    def add(self, debt: Debt) -> Debt: ...

    @abstractmethod
    def update(self, debt: Debt) -> Debt: ...

    @abstractmethod
    def delete(self, account_id: int, debt_id: UUID) -> bool: ...


class PlanRepository(ABC):
    @abstractmethod
    def list(self, account_id: int) -> list[MonthPlan]: ...

    @abstractmethod
    def get(self, account_id: int, month: str) -> MonthPlan | None: ...

    @abstractmethod
    def save(self, account_id: int, plan: MonthPlan) -> MonthPlan: ...


class SettingsRepository(ABC):
    @abstractmethod
    def get(self, account_id: int) -> LedgerSettings: ...

    @abstractmethod
    def save(self, account_id: int, settings: LedgerSettings) -> LedgerSettings: ...


class SpreadsheetBuilder(ABC):
    @abstractmethod
    def build(self, *, month: str, lang: str, transactions: list[Transaction], debts: list[Debt], settings: LedgerSettings) -> bytes: ...


class DocumentSender(ABC):
    @abstractmethod
    def send(self, chat_id: int, filename: str, content: bytes, caption: str) -> bool: ...
