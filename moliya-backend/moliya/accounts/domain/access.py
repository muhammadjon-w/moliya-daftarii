"""Obuna holati qoidalari: sinov, faol obuna yoki tugagan."""
import math
from dataclasses import dataclass
from datetime import datetime

from moliya.shared.domain.clock import add_months

DAY_SECONDS = 86400


@dataclass(frozen=True)
class Access:
    state: str  # "trial" | "active" | "expired"
    trial_ends_at: datetime
    paid_until: datetime | None
    days_left: int
    can_write: bool


def access_of(trial_ends_at: datetime, paid_until: datetime | None, now: datetime) -> Access:
    if paid_until and paid_until > now:
        days = math.ceil((paid_until - now).total_seconds() / DAY_SECONDS)
        return Access("active", trial_ends_at, paid_until, days, True)
    if trial_ends_at > now:
        days = math.ceil((trial_ends_at - now).total_seconds() / DAY_SECONDS)
        return Access("trial", trial_ends_at, paid_until, days, True)
    return Access("expired", trial_ends_at, paid_until, 0, False)


def extended_until(trial_ends_at: datetime, paid_until: datetime | None, months: int, now: datetime) -> datetime:
    """To'lovdan keyingi yangi obuna muddati. Sinov paytida to'lansa, sinov tugaganidan boshlab hisoblanadi."""
    start = max(d for d in (paid_until, now, trial_ends_at) if d is not None)
    return add_months(start, months)


def reduced_until(paid_until: datetime | None, months: int) -> datetime | None:
    """To'lov qaytarilganda obunani qisqartiradi."""
    return add_months(paid_until, -months) if paid_until else None
