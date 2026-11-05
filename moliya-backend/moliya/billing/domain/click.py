"""Click SHOP API (Prepare / Complete) qoidalari. Hujjat: https://docs.click.uz/click-api-request/"""
import hashlib
from abc import ABC, abstractmethod
from decimal import Decimal, InvalidOperation

from moliya.billing.domain.entities import ClickTransaction, Order

E = {
    "SIGN": (-1, "SIGN CHECK FAILED!"),
    "AMOUNT": (-2, "Incorrect parameter amount"),
    "ACTION": (-3, "Action not found"),
    "PAID": (-4, "Already paid"),
    "USER": (-5, "User does not exist"),
    "TX": (-6, "Transaction does not exist"),
    "UPDATE": (-7, "Failed to update user"),
    "REQUEST": (-8, "Error in request from click"),
    "CANCELLED": (-9, "Transaction cancelled"),
}


class ClickStore(ABC):
    @abstractmethod
    def get_order(self, order_id: int) -> Order | None: ...
    @abstractmethod
    def get_tx_by_click_id(self, click_trans_id: int) -> ClickTransaction | None: ...
    @abstractmethod
    def get_tx(self, tx_id: int) -> ClickTransaction | None: ...
    @abstractmethod
    def insert_tx(self, click_trans_id: int, order_id: int, amount: Decimal) -> ClickTransaction: ...
    @abstractmethod
    def set_tx_status(self, tx_id: int, status: str) -> None: ...
    @abstractmethod
    def activate_order(self, order_id: int) -> None: ...


def expected_sign(p: dict, secret: str) -> str:
    prepare_id = p.get("merchant_prepare_id", "") if p.get("action") == "1" else ""
    raw = f"{p.get('click_trans_id')}{p.get('service_id')}{secret}{p.get('merchant_trans_id')}{prepare_id}{p.get('amount')}{p.get('action')}{p.get('sign_time')}"
    return hashlib.md5(raw.encode()).hexdigest()


def _int(v) -> int | None:
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def process(store: ClickStore, p: dict, secret: str, service_id: str) -> dict:
    base = {"click_trans_id": _int(p.get("click_trans_id")) or 0, "merchant_trans_id": p.get("merchant_trans_id", "")}

    def fail(key, **extra):
        code, note = E[key]
        return {**base, **extra, "error": code, "error_note": note}

    required = ("click_trans_id", "service_id", "merchant_trans_id", "amount", "action", "sign_time", "sign_string")
    if any(not p.get(k) and p.get(k) != "0" for k in required):
        return fail("REQUEST")
    if p["action"] not in ("0", "1"):
        return fail("ACTION")
    if service_id and p["service_id"] != service_id:
        return fail("REQUEST")
    if expected_sign(p, secret) != str(p["sign_string"]).lower():
        return fail("SIGN")

    oid = _int(p["merchant_trans_id"])
    order = store.get_order(oid) if oid and oid > 0 else None
    if not order:
        return fail("USER")
    try:
        amount = Decimal(str(p["amount"]))
    except InvalidOperation:
        return fail("AMOUNT")
    if abs(amount - Decimal(order.amount_uzs)) > Decimal("0.01"):
        return fail("AMOUNT")

    click_id = _int(p["click_trans_id"])
    if p["action"] == "0":
        if order.status == "paid":
            return fail("PAID")
        if order.status == "cancelled":
            return fail("CANCELLED")
        existing = store.get_tx_by_click_id(click_id)
        if existing:
            if existing.status == "cancelled":
                return fail("CANCELLED")
            if existing.status == "completed":
                return fail("PAID")
            return {**base, "merchant_prepare_id": existing.id, "error": 0, "error_note": "Success"}
        tx = store.insert_tx(click_id, order.id, amount)
        return {**base, "merchant_prepare_id": tx.id, "error": 0, "error_note": "Success"}

    prepare_id = _int(p.get("merchant_prepare_id"))
    tx = store.get_tx(prepare_id) if prepare_id is not None else None
    if not tx or tx.click_trans_id != click_id or tx.order_id != order.id:
        return fail("TX")
    if tx.status == "completed":
        return fail("PAID", merchant_confirm_id=tx.id)
    if tx.status == "cancelled":
        return fail("CANCELLED")
    if (_int(p.get("error")) or 0) < 0:
        store.set_tx_status(tx.id, "cancelled")
        return fail("CANCELLED")
    if order.status == "paid":
        return fail("PAID")
    try:
        store.set_tx_status(tx.id, "completed")
        store.activate_order(order.id)
    except Exception:  # noqa: BLE001
        return fail("UPDATE")
    return {**base, "merchant_confirm_id": tx.id, "error": 0, "error_note": "Success"}
