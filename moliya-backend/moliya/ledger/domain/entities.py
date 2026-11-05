"""Hisob yozuvlari: domen obyektlari va ularning o'zgarmas qoidalari."""
from __future__ import annotations

import re
from dataclasses import dataclass, field, replace
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from moliya.ledger.domain.catalog import ITEMS
from moliya.shared.domain.clock import add_months
from moliya.shared.domain.errors import ValidationFailed

TX_TYPES = ("income", "expense")
GROUPS = ("inc", "pay", "exp", "debt")
EXPENSE_GROUPS = ("pay", "exp", "debt")
CURRENCIES = ("UZS", "USD")
METHODS = ("cash", "card", "bank")
DEBT_STATUSES = ("", "active", "paid", "overdue")
MONTH_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])$")
PLAN_KEY_RE = re.compile(r"^(inc|pay|exp|debt):[\w'\- .]{1,100}$", re.UNICODE)
MAX_AMOUNT = Decimal("1000000000000")


def _money(value, name: str, allow_zero: bool = False) -> Decimal:
    try:
        d = Decimal(str(value)).quantize(Decimal("0.01"))
    except Exception as exc:  # noqa: BLE001
        raise ValidationFailed(f"{name}: raqam bo'lishi kerak.", field=name) from exc
    if d < 0 or (d == 0 and not allow_zero) or d > MAX_AMOUNT:
        raise ValidationFailed(f"{name}: 0 dan katta bo'lishi kerak.", field=name)
    return d


@dataclass
class Transaction:
    account_id: int
    type: str
    group: str
    item: str
    category: str
    amount: Decimal
    currency: str
    date: date
    method: str
    note: str = ""
    id: UUID | None = None
    created_at: datetime | None = None

    def __post_init__(self):
        if self.type not in TX_TYPES:
            raise ValidationFailed("Turi noto'g'ri.", field="type")
        if self.type == "income":
            self.group = "inc"
        elif self.group not in EXPENSE_GROUPS:
            raise ValidationFailed("Guruh noto'g'ri.", field="group")
        self.item = (self.item or "").strip()[:120]
        if not self.item:
            raise ValidationFailed("Moddani tanlang yoki yozing.", field="item")
        known = ITEMS.get(self.item)
        if known:
            # katalogdagi modda bo'lsa, toifa va guruh katalogdan olinadi
            self.category = known[0]
            if self.type == "expense":
                self.group = known[1] if known[1] != "inc" else self.group
        self.category = (self.category or self.item).strip()[:120]
        self.amount = _money(self.amount, "amount")
        if self.currency not in CURRENCIES:
            raise ValidationFailed("Valyuta noto'g'ri.", field="currency")
        if self.method not in METHODS:
            raise ValidationFailed("To'lov usuli noto'g'ri.", field="method")
        self.note = (self.note or "").strip()[:1000]

    def amount_uzs(self, usd_rate: Decimal) -> Decimal:
        return self.amount * usd_rate if self.currency == "USD" else self.amount

    @property
    def signed_sign(self) -> int:
        return 1 if self.type == "income" else -1


@dataclass
class DebtSummary:
    principal: Decimal
    paid: Decimal
    remaining: Decimal
    months: int
    monthly: Decimal
    status: str


@dataclass
class Debt:
    account_id: int
    lender: str
    principal: Decimal
    paid: Decimal = Decimal("0")
    months: int = 0
    status: str = ""
    date: date | None = None
    pay_date: date | None = None
    deadline: date | None = None
    note: str = ""
    id: UUID | None = None
    created_at: datetime | None = None

    def __post_init__(self):
        self.lender = (self.lender or "").strip()[:200]
        self.principal = _money(self.principal, "principal")
        self.paid = _money(self.paid or 0, "paid", allow_zero=True)
        try:
            self.months = int(self.months or 0)
        except (TypeError, ValueError) as exc:
            raise ValidationFailed("Oylar soni butun son bo'lishi kerak.", field="months") from exc
        if not 0 <= self.months <= 600:
            raise ValidationFailed("Oylar soni noto'g'ri.", field="months")
        if self.status not in DEBT_STATUSES:
            raise ValidationFailed("Holat noto'g'ri.", field="status")
        self.note = (self.note or "").strip()[:1000]

    def summary(self, today: date) -> DebtSummary:
        remaining = max(self.principal - self.paid, Decimal("0"))
        monthly = (remaining / self.months).quantize(Decimal("0.01")) if self.months else Decimal("0")
        status = self.status
        if not status:
            due = self.deadline
            status = "paid" if remaining <= 0 else ("overdue" if due and due < today else "active")
        return DebtSummary(self.principal, self.paid, remaining, self.months, monthly, status)

    def with_payment(self, amount) -> "Debt":
        """To'lovni qo'shadi.

        `months` — qolgan oylar soni. To'liq oylik to'lov qilinsa (qarz hali yopilmagan bo'lsa)
        qolgan oylar bittaga kamayadi va keyingi to'lov sanasi bir oyga suriladi. Qisman to'lovda — o'zgarmaydi.
        """
        amount = _money(amount, "amount")
        monthly_before = (max(self.principal - self.paid, Decimal("0")) / self.months) if self.months else Decimal("0")
        new = replace(self, paid=self.paid + amount)
        if new.status != "paid" and new.principal - new.paid <= 0:
            new.status = ""
        full_installment = not self.months or amount + Decimal("1") >= monthly_before
        if new.principal - new.paid > 0 and full_installment:
            if new.months:
                new.months -= 1
            if new.pay_date:
                new.pay_date = add_months(new.pay_date, 1)
        return new


@dataclass
class MonthPlan:
    month: str
    values: dict[str, Decimal] = field(default_factory=dict)

    def __post_init__(self):
        if not MONTH_RE.match(self.month or ""):
            raise ValidationFailed("Oy YYYY-MM ko'rinishida bo'lishi kerak.", field="month")
        clean: dict[str, Decimal] = {}
        for key, value in (self.values or {}).items():
            if not PLAN_KEY_RE.match(str(key)):
                raise ValidationFailed(f"Reja kaliti noto'g'ri: {key}", field="values")
            d = _money(value, "values", allow_zero=True)
            if d > 0:
                clean[str(key)] = d
        self.values = clean


@dataclass
class LedgerSettings:
    usd_rate: Decimal = Decimal("12000")
    opening_balance: Decimal = Decimal("0")

    def __post_init__(self):
        self.usd_rate = _money(self.usd_rate, "usdRate")
        try:
            self.opening_balance = Decimal(str(self.opening_balance)).quantize(Decimal("0.01"))
        except Exception as exc:  # noqa: BLE001
            raise ValidationFailed("Boshlang'ich qoldiq raqam bo'lishi kerak.", field="openingBalance") from exc
