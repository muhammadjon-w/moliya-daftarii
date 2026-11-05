"""Hisobotlar uchun sof hisob-kitoblar (Excel eksport ishlatadi)."""
from dataclasses import dataclass
from decimal import Decimal

from moliya.ledger.domain.entities import Transaction

ZERO = Decimal("0")


@dataclass
class MonthTotals:
    inc: Decimal = ZERO
    pay: Decimal = ZERO
    exp: Decimal = ZERO
    debt: Decimal = ZERO

    @property
    def out(self) -> Decimal:
        return self.pay + self.exp + self.debt

    @property
    def net(self) -> Decimal:
        return self.inc - self.out


def month_of(tx: Transaction) -> str:
    return f"{tx.date.year:04d}-{tx.date.month:02d}"


def totals(transactions: list[Transaction], usd_rate: Decimal) -> MonthTotals:
    t = MonthTotals()
    for tx in transactions:
        setattr(t, tx.group, getattr(t, tx.group) + tx.amount_uzs(usd_rate))
    return t


def balance_before(transactions: list[Transaction], month: str, usd_rate: Decimal, opening: Decimal) -> Decimal:
    total = opening
    for tx in transactions:
        if month_of(tx) < month:
            total += tx.signed_sign * tx.amount_uzs(usd_rate)
    return total
