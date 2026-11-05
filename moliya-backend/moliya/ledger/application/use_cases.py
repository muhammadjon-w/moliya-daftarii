"""Hisob bilan bog'liq ssenariylar. Har biri bitta foydalanuvchi amaliga mos keladi."""
from dataclasses import replace
from datetime import date
from uuid import UUID

from moliya.accounts.application.use_cases import access_for, ensure_can_write
from moliya.accounts.domain.entities import Account
from moliya.ledger.application.ports import (
    DebtRepository,
    DocumentSender,
    PlanRepository,
    SettingsRepository,
    SpreadsheetBuilder,
    TransactionRepository,
)
from moliya.ledger.domain.entities import MONTH_RE, Debt, LedgerSettings, MonthPlan, Transaction
from moliya.shared.application.unit_of_work import UnitOfWork
from moliya.shared.domain.errors import ExternalServiceError, NotFound, ValidationFailed


class LedgerService:
    """Hisobning barcha amallari. Portlar orqali ishlaydi, Django'ni bilmaydi."""

    def __init__(
        self,
        transactions: TransactionRepository,
        debts: DebtRepository,
        plans: PlanRepository,
        settings: SettingsRepository,
        uow: UnitOfWork,
        clock=None,
    ):
        self.transactions, self.debts, self.plans, self.settings, self.uow = transactions, debts, plans, settings, uow
        from moliya.shared.domain.clock import utcnow

        self._now = clock or utcnow

    # ---------- o'qish ----------
    def state(self, account: Account) -> dict:
        return {
            "access": access_for(account, self._now()),
            "transactions": self.transactions.list(account.id),
            "debts": self.debts.list(account.id),
            "plans": self.plans.list(account.id),
            "settings": self.settings.get(account.id),
        }

    # ---------- yozuvlar ----------
    def create_transaction(self, account: Account, data: dict) -> Transaction:
        ensure_can_write(account, self._now())
        return self.transactions.add(Transaction(account_id=account.id, **data))

    def update_transaction(self, account: Account, tx_id: UUID, data: dict) -> Transaction:
        ensure_can_write(account, self._now())
        current = self.transactions.get(account.id, tx_id)
        if not current:
            raise NotFound("Yozuv topilmadi.")
        merged = {**_tx_fields(current), **data}
        updated = Transaction(account_id=account.id, id=current.id, created_at=current.created_at, **merged)
        return self.transactions.update(updated)

    def delete_transaction(self, account: Account, tx_id: UUID) -> None:
        # O'chirish obuna tugaganda ham ruxsat etiladi: foydalanuvchi o'z ma'lumotini tozalay oladi.
        if not self.transactions.delete(account.id, tx_id):
            raise NotFound("Yozuv topilmadi.")

    # ---------- qarzlar ----------
    def create_debt(self, account: Account, data: dict) -> Debt:
        ensure_can_write(account, self._now())
        return self.debts.add(Debt(account_id=account.id, **data))

    def update_debt(self, account: Account, debt_id: UUID, data: dict) -> Debt:
        ensure_can_write(account, self._now())
        current = self.debts.get(account.id, debt_id)
        if not current:
            raise NotFound("Qarz topilmadi.")
        merged = {**_debt_fields(current), **data}
        return self.debts.update(Debt(account_id=account.id, id=current.id, created_at=current.created_at, **merged))

    def delete_debt(self, account: Account, debt_id: UUID) -> None:
        if not self.debts.delete(account.id, debt_id):
            raise NotFound("Qarz topilmadi.")

    def record_debt_payment(self, account: Account, debt_id: UUID, amount, on: date, log_transaction: bool) -> tuple[Debt, Transaction | None]:
        """Qarzga to'lov: qarz kamayadi va xohlasa shu oy chiqimlariga yoziladi. Ikkalasi bitta tranzaksiyada."""
        ensure_can_write(account, self._now())
        with self.uow.atomic():
            debt = self.debts.get(account.id, debt_id, for_update=True)
            if not debt:
                raise NotFound("Qarz topilmadi.")
            summary = debt.summary(on)
            if summary.remaining <= 0:
                raise ValidationFailed("Bu qarz to'liq to'langan.", field="amount")
            updated = self.debts.update(debt.with_payment(amount))
            tx = None
            if log_transaction:
                tx = self.transactions.add(Transaction(
                    account_id=account.id, type="expense", group="debt", item="debt", category="debts",
                    amount=amount, currency="UZS", date=on, method="cash", note=debt.lender,
                ))
        return updated, tx

    # ---------- reja ----------
    def save_plan(self, account: Account, month: str, values: dict) -> MonthPlan:
        ensure_can_write(account, self._now())
        return self.plans.save(account.id, MonthPlan(month=month, values=values))

    def copy_previous_plan(self, account: Account, month: str) -> MonthPlan:
        ensure_can_write(account, self._now())
        if not MONTH_RE.match(month or ""):
            raise ValidationFailed("Oy YYYY-MM ko'rinishida bo'lishi kerak.", field="month")
        y, m = int(month[:4]), int(month[5:])
        prev = f"{y - 1:04d}-12" if m == 1 else f"{y:04d}-{m - 1:02d}"
        source = self.plans.get(account.id, prev)
        if not source or not source.values:
            raise NotFound("O'tgan oyda reja yo'q.")
        return self.plans.save(account.id, MonthPlan(month=month, values=dict(source.values)))

    # ---------- sozlamalar ----------
    def update_settings(self, account: Account, data: dict) -> LedgerSettings:
        current = self.settings.get(account.id)
        return self.settings.save(account.id, replace(current, **data) if data else current)


class ExportLedger:
    def __init__(self, ledger: LedgerService, builder: SpreadsheetBuilder, sender: DocumentSender):
        self._ledger, self._builder, self._sender = ledger, builder, sender

    def execute(self, account: Account, month: str) -> str:
        if not MONTH_RE.match(month or ""):
            raise ValidationFailed("Oy YYYY-MM ko'rinishida bo'lishi kerak.", field="month")
        content = self._builder.build(
            month=month,
            lang=account.language_code or "uz",
            transactions=self._ledger.transactions.list(account.id),
            debts=self._ledger.debts.list(account.id),
            settings=self._ledger.settings.get(account.id),
        )
        filename = f"moliya-daftari-{month}.xlsx"
        if not self._sender.send(account.id, filename, content, "Moliya daftari — Excel hisobot"):
            raise ExternalServiceError("Botga /start yozing, keyin qayta urinib ko'ring.")
        return filename


def _tx_fields(tx: Transaction) -> dict:
    return {k: getattr(tx, k) for k in ("type", "group", "item", "category", "amount", "currency", "date", "method", "note")}


def _debt_fields(d: Debt) -> dict:
    return {k: getattr(d, k) for k in ("lender", "principal", "paid", "months", "status", "date", "pay_date", "deadline", "note")}
