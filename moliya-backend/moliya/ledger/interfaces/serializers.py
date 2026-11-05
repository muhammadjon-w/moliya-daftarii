"""Kiruvchi ma'lumotni tekshirish (DRF) va chiquvchi JSON (camelCase) tayyorlash."""
from decimal import Decimal

from rest_framework import serializers

from moliya.ledger.domain.entities import CURRENCIES, DEBT_STATUSES, EXPENSE_GROUPS, METHODS, TX_TYPES, Debt, LedgerSettings, MonthPlan, Transaction

MAX = Decimal("1000000000000")


class TransactionIn(serializers.Serializer):
    type = serializers.ChoiceField(choices=TX_TYPES)
    group = serializers.ChoiceField(choices=("inc",) + EXPENSE_GROUPS, required=False)
    item = serializers.CharField(max_length=120)
    category = serializers.CharField(max_length=120, required=False, allow_blank=True)
    amount = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=Decimal("0.01"), max_value=MAX)
    currency = serializers.ChoiceField(choices=CURRENCIES, default="UZS")
    date = serializers.DateField()
    method = serializers.ChoiceField(choices=METHODS, default="cash")
    note = serializers.CharField(max_length=1000, required=False, allow_blank=True, default="")

    def to_domain(self) -> dict:
        d = dict(self.validated_data)
        d.setdefault("group", "inc" if d["type"] == "income" else "exp")
        d.setdefault("category", "")
        return d


class DebtIn(serializers.Serializer):
    lender = serializers.CharField(max_length=200, required=False, allow_blank=True, default="")
    principal = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=Decimal("0.01"), max_value=MAX)
    paid = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=Decimal("0"), max_value=MAX, default=Decimal("0"))
    months = serializers.IntegerField(min_value=0, max_value=600, default=0)
    status = serializers.ChoiceField(choices=DEBT_STATUSES, default="", allow_blank=True)
    date = serializers.DateField(required=False, allow_null=True, default=None)
    payDate = serializers.DateField(required=False, allow_null=True, default=None)
    deadline = serializers.DateField(required=False, allow_null=True, default=None)
    note = serializers.CharField(max_length=1000, required=False, allow_blank=True, default="")

    def to_domain(self) -> dict:
        d = dict(self.validated_data)
        d["pay_date"] = d.pop("payDate", None)
        return d


class DebtPaymentIn(serializers.Serializer):
    amount = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=Decimal("0.01"), max_value=MAX)
    date = serializers.DateField()
    logTransaction = serializers.BooleanField(default=True)


class PlanIn(serializers.Serializer):
    values = serializers.DictField(child=serializers.DecimalField(max_digits=18, decimal_places=2, min_value=Decimal("0"), max_value=MAX), allow_empty=True)


class SettingsIn(serializers.Serializer):
    usdRate = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=Decimal("1"), max_value=MAX, required=False)
    openingBalance = serializers.DecimalField(max_digits=18, decimal_places=2, min_value=-MAX, max_value=MAX, required=False)

    def to_domain(self) -> dict:
        d = {}
        if "usdRate" in self.validated_data:
            d["usd_rate"] = self.validated_data["usdRate"]
        if "openingBalance" in self.validated_data:
            d["opening_balance"] = self.validated_data["openingBalance"]
        return d


class ExportIn(serializers.Serializer):
    month = serializers.RegexField(r"^\d{4}-(0[1-9]|1[0-2])$")


# ---------- chiqish ----------
def num(v: Decimal) -> float:
    return float(v)


def tx_out(t: Transaction) -> dict:
    return {
        "id": str(t.id), "type": t.type, "group": t.group, "item": t.item, "category": t.category,
        "amount": num(t.amount), "currency": t.currency, "date": t.date.isoformat(), "method": t.method,
        "note": t.note, "createdAt": t.created_at.isoformat() if t.created_at else None,
    }


def debt_out(d: Debt) -> dict:
    return {
        "id": str(d.id), "lender": d.lender, "principal": num(d.principal), "paid": num(d.paid), "months": d.months,
        "status": d.status, "date": d.date.isoformat() if d.date else None,
        "payDate": d.pay_date.isoformat() if d.pay_date else None,
        "deadline": d.deadline.isoformat() if d.deadline else None, "note": d.note,
        "createdAt": d.created_at.isoformat() if d.created_at else None,
    }


def plans_out(plans: list[MonthPlan]) -> dict:
    return {p.month: {k: num(v) for k, v in p.values.items()} for p in plans}


def settings_out(s: LedgerSettings) -> dict:
    return {"usdRate": num(s.usd_rate), "openingBalance": num(s.opening_balance)}
