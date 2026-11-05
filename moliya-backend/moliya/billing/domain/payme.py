"""Payme Merchant API (JSON-RPC 2.0) qoidalari.
Hujjat: https://developer.help.paycom.uz/metody-merchant-api/
Ma'lumotlar ombori PaymeStore porti orqali beriladi, shuning uchun bu modul toza va testlanadi.
"""
import base64
import binascii
import json
from abc import ABC, abstractmethod

from moliya.billing.domain.entities import Order, PaymeTransaction

TIMEOUT_MS = 43_200_000  # 12 soat

MSG = {
    "amount": {"ru": "Неверная сумма", "uz": "Noto'g'ri summa", "en": "Incorrect amount"},
    "order": {"ru": "Заказ не найден", "uz": "Buyurtma topilmadi", "en": "Order not found"},
    "order_state": {"ru": "Заказ уже оплачен или отменён", "uz": "Buyurtma allaqachon to'langan yoki bekor qilingan", "en": "Order is already paid or cancelled"},
    "busy": {"ru": "Заказ ожидает оплаты в другой транзакции", "uz": "Buyurtma boshqa tranzaksiyada to'lanmoqda", "en": "Order has another pending transaction"},
    "tx_not_found": {"ru": "Транзакция не найдена", "uz": "Tranzaksiya topilmadi", "en": "Transaction not found"},
    "cant_perform": {"ru": "Невозможно выполнить операцию", "uz": "Amalni bajarib bo'lmaydi", "en": "Unable to perform operation"},
    "method": {"ru": "Метод не найден", "uz": "Metod topilmadi", "en": "Method not found"},
    "auth": {"ru": "Недостаточно привилегий", "uz": "Ruxsat yo'q", "en": "Insufficient privileges"},
    "parse": {"ru": "Ошибка разбора JSON", "uz": "JSON xato", "en": "Parse error"},
    "system": {"ru": "Системная ошибка", "uz": "Tizim xatosi", "en": "System error"},
}


class PaymeError(Exception):
    def __init__(self, code: int, msg_key: str, data: str | None = None):
        super().__init__(MSG[msg_key]["en"])
        self.code, self.message, self.data = code, MSG[msg_key], data


class PaymeStore(ABC):
    @abstractmethod
    def get_order(self, order_id: int) -> Order | None: ...
    @abstractmethod
    def get_tx(self, tx_id: str) -> PaymeTransaction | None: ...
    @abstractmethod
    def get_open_tx_for_order(self, order_id: int) -> PaymeTransaction | None: ...
    @abstractmethod
    def insert_tx(self, tx: PaymeTransaction) -> None: ...
    @abstractmethod
    def update_tx(self, tx_id: str, **fields) -> None: ...
    @abstractmethod
    def activate_order(self, order_id: int) -> None: ...
    @abstractmethod
    def revoke_order(self, order_id: int) -> None: ...
    @abstractmethod
    def list_tx(self, start: int, end: int) -> list[PaymeTransaction]: ...


def check_auth(header: str | None, key: str) -> bool:
    if not header or not key or not header.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(header[6:]).decode()
    except (binascii.Error, UnicodeDecodeError):
        return False
    login, _, password = decoded.partition(":")
    return bool(login) and password == key


def _order_id(account) -> int | None:
    try:
        n = int((account or {}).get("order_id"))
        return n if n > 0 else None
    except (TypeError, ValueError):
        return None


def _valid_order(store: PaymeStore, params: dict) -> Order:
    oid = _order_id(params.get("account"))
    order = store.get_order(oid) if oid else None
    if not order:
        raise PaymeError(-31050, "order", "order_id")
    if order.status != "new":
        raise PaymeError(-31051, "order_state", "order_id")
    try:
        amount = int(params.get("amount"))
    except (TypeError, ValueError):
        amount = -1
    if amount != order.amount_uzs * 100:
        raise PaymeError(-31001, "amount")
    return order


def handle(store: PaymeStore, method: str, params: dict, now: int):
    if method == "CheckPerformTransaction":
        _valid_order(store, params)
        return {"allow": True}

    if method == "CreateTransaction":
        tx_id = str(params.get("id") or "")
        existing = store.get_tx(tx_id)
        if existing:
            if existing.state != 1:
                raise PaymeError(-31008, "cant_perform")
            if now - existing.create_time > TIMEOUT_MS:
                store.update_tx(tx_id, state=-1, reason=4, cancel_time=now)
                store.revoke_order(existing.order_id)
                raise PaymeError(-31008, "cant_perform")
            return {"create_time": existing.create_time, "transaction": existing.id, "state": existing.state}
        order = _valid_order(store, params)
        open_tx = store.get_open_tx_for_order(order.id)
        if open_tx and open_tx.id != tx_id:
            raise PaymeError(-31050, "busy", "order_id")
        payme_time = int(params.get("time") or now)
        if now - payme_time > TIMEOUT_MS:
            raise PaymeError(-31008, "cant_perform")
        store.insert_tx(PaymeTransaction(id=tx_id, order_id=order.id, amount=int(params["amount"]), state=1, payme_time=payme_time, create_time=now))
        return {"create_time": now, "transaction": tx_id, "state": 1}

    if method == "PerformTransaction":
        tx = store.get_tx(str(params.get("id") or ""))
        if not tx:
            raise PaymeError(-31003, "tx_not_found")
        if tx.state == 2:
            return {"transaction": tx.id, "perform_time": tx.perform_time, "state": 2}
        if tx.state != 1:
            raise PaymeError(-31008, "cant_perform")
        if now - tx.create_time > TIMEOUT_MS:
            store.update_tx(tx.id, state=-1, reason=4, cancel_time=now)
            store.revoke_order(tx.order_id)
            raise PaymeError(-31008, "cant_perform")
        store.update_tx(tx.id, state=2, perform_time=now)
        store.activate_order(tx.order_id)
        return {"transaction": tx.id, "perform_time": now, "state": 2}

    if method == "CancelTransaction":
        tx = store.get_tx(str(params.get("id") or ""))
        if not tx:
            raise PaymeError(-31003, "tx_not_found")
        if tx.state in (-1, -2):
            return {"transaction": tx.id, "cancel_time": tx.cancel_time, "state": tx.state}
        reason = int(params.get("reason") or 0) or None
        new_state = -1 if tx.state == 1 else -2
        store.update_tx(tx.id, state=new_state, cancel_time=now, reason=reason)
        store.revoke_order(tx.order_id)
        return {"transaction": tx.id, "cancel_time": now, "state": new_state}

    if method == "CheckTransaction":
        tx = store.get_tx(str(params.get("id") or ""))
        if not tx:
            raise PaymeError(-31003, "tx_not_found")
        return {"create_time": tx.create_time, "perform_time": tx.perform_time, "cancel_time": tx.cancel_time,
                "transaction": tx.id, "state": tx.state, "reason": tx.reason}

    if method == "GetStatement":
        items = store.list_tx(int(params.get("from") or 0), int(params.get("to") or now))
        return {"transactions": [{
            "id": t.id, "time": t.payme_time, "amount": t.amount, "account": {"order_id": str(t.order_id)},
            "create_time": t.create_time, "perform_time": t.perform_time, "cancel_time": t.cancel_time,
            "transaction": t.id, "state": t.state, "reason": t.reason,
        } for t in items]}

    raise PaymeError(-32601, "method", method)


def process_request(store: PaymeStore, auth_header: str | None, key: str, raw_body: bytes | str, now: int) -> dict:
    try:
        body = json.loads(raw_body)
    except (ValueError, TypeError):
        return {"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": MSG["parse"]}}
    rid = body.get("id") if isinstance(body, dict) else None
    if not check_auth(auth_header, key):
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32504, "message": MSG["auth"]}}
    if not isinstance(body, dict) or not body.get("method"):
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": -32600, "message": MSG["method"]}}
    try:
        return {"jsonrpc": "2.0", "id": rid, "result": handle(store, body["method"], body.get("params") or {}, now)}
    except PaymeError as e:
        return {"jsonrpc": "2.0", "id": rid, "error": {"code": e.code, "message": e.message, "data": e.data}}
