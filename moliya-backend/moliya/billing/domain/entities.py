from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


@dataclass
class Order:
    id: int
    account_id: int
    months: int
    amount_uzs: int
    provider: str | None
    status: str  # new | paid | cancelled
    created_at: datetime | None = None
    paid_at: datetime | None = None


@dataclass
class PaymeTransaction:
    id: str
    order_id: int
    amount: int  # tiyin
    state: int  # 1 yaratilgan, 2 bajarilgan, -1 / -2 bekor
    payme_time: int
    create_time: int
    perform_time: int = 0
    cancel_time: int = 0
    reason: int | None = None


@dataclass
class ClickTransaction:
    id: int
    click_trans_id: int
    order_id: int
    amount: Decimal
    status: str  # prepared | completed | cancelled
