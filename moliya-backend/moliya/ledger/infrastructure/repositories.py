from decimal import Decimal
from uuid import UUID

from moliya.ledger.application.ports import DebtRepository, PlanRepository, SettingsRepository, TransactionRepository
from moliya.ledger.domain.entities import Debt, LedgerSettings, MonthPlan, Transaction
from moliya.ledger.infrastructure.models import DebtModel, PlanModel, SettingsModel, TransactionModel

TX_FIELDS = ("type", "group", "item", "category", "amount", "currency", "date", "method", "note")
DEBT_FIELDS = ("lender", "principal", "paid", "months", "status", "date", "pay_date", "deadline", "note")


def _tx(m: TransactionModel) -> Transaction:
    return Transaction(account_id=m.account_id, id=m.id, created_at=m.created_at, **{f: getattr(m, f) for f in TX_FIELDS})


def _debt(m: DebtModel) -> Debt:
    return Debt(account_id=m.account_id, id=m.id, created_at=m.created_at, **{f: getattr(m, f) for f in DEBT_FIELDS})


class DjangoTransactionRepository(TransactionRepository):
    def list(self, account_id: int) -> list[Transaction]:
        return [_tx(m) for m in TransactionModel.objects.filter(account_id=account_id)]

    def get(self, account_id: int, tx_id: UUID) -> Transaction | None:
        m = TransactionModel.objects.filter(account_id=account_id, pk=tx_id).first()
        return _tx(m) if m else None

    def add(self, tx: Transaction) -> Transaction:
        m = TransactionModel.objects.create(account_id=tx.account_id, **{f: getattr(tx, f) for f in TX_FIELDS})
        return _tx(m)

    def update(self, tx: Transaction) -> Transaction:
        TransactionModel.objects.filter(account_id=tx.account_id, pk=tx.id).update(**{f: getattr(tx, f) for f in TX_FIELDS})
        return self.get(tx.account_id, tx.id)

    def delete(self, account_id: int, tx_id: UUID) -> bool:
        deleted, _ = TransactionModel.objects.filter(account_id=account_id, pk=tx_id).delete()
        return deleted > 0


class DjangoDebtRepository(DebtRepository):
    def list(self, account_id: int) -> list[Debt]:
        return [_debt(m) for m in DebtModel.objects.filter(account_id=account_id)]

    def get(self, account_id: int, debt_id: UUID, for_update: bool = False) -> Debt | None:
        qs = DebtModel.objects.filter(account_id=account_id, pk=debt_id)
        m = (qs.select_for_update() if for_update else qs).first()
        return _debt(m) if m else None

    def add(self, debt: Debt) -> Debt:
        return _debt(DebtModel.objects.create(account_id=debt.account_id, **{f: getattr(debt, f) for f in DEBT_FIELDS}))

    def update(self, debt: Debt) -> Debt:
        DebtModel.objects.filter(account_id=debt.account_id, pk=debt.id).update(**{f: getattr(debt, f) for f in DEBT_FIELDS})
        return self.get(debt.account_id, debt.id)

    def delete(self, account_id: int, debt_id: UUID) -> bool:
        deleted, _ = DebtModel.objects.filter(account_id=account_id, pk=debt_id).delete()
        return deleted > 0


class DjangoPlanRepository(PlanRepository):
    @staticmethod
    def _entity(m: PlanModel) -> MonthPlan:
        return MonthPlan(month=m.month, values={k: Decimal(str(v)) for k, v in (m.values or {}).items()})

    def list(self, account_id: int) -> list[MonthPlan]:
        return [self._entity(m) for m in PlanModel.objects.filter(account_id=account_id).order_by("month")]

    def get(self, account_id: int, month: str) -> MonthPlan | None:
        m = PlanModel.objects.filter(account_id=account_id, month=month).first()
        return self._entity(m) if m else None

    def save(self, account_id: int, plan: MonthPlan) -> MonthPlan:
        PlanModel.objects.update_or_create(
            account_id=account_id, month=plan.month,
            defaults={"values": {k: str(v) for k, v in plan.values.items()}},
        )
        return plan


class DjangoSettingsRepository(SettingsRepository):
    def get(self, account_id: int) -> LedgerSettings:
        m = SettingsModel.objects.filter(account_id=account_id).first()
        return LedgerSettings(usd_rate=m.usd_rate, opening_balance=m.opening_balance) if m else LedgerSettings()

    def save(self, account_id: int, settings: LedgerSettings) -> LedgerSettings:
        SettingsModel.objects.update_or_create(
            account_id=account_id,
            defaults={"usd_rate": settings.usd_rate, "opening_balance": settings.opening_balance},
        )
        return settings
