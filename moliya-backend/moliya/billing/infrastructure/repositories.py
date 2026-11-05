import base64
import hashlib
import logging
import time
from decimal import Decimal
from urllib.parse import urlencode

import requests
from django.utils import timezone

from moliya.billing.application.ports import ClickInvoiceGateway, OrderRepository, PaymentLinks
from moliya.billing.application.use_cases import BillingService
from moliya.billing.domain.click import ClickStore
from moliya.billing.domain.entities import ClickTransaction, Order, PaymeTransaction
from moliya.billing.domain.payme import PaymeStore
from moliya.billing.infrastructure.models import ClickInvoiceModel, ClickTransactionModel, OrderModel, PaymeTransactionModel
from moliya.shared.domain.errors import ExternalServiceError

log = logging.getLogger(__name__)


def _order(m: OrderModel) -> Order:
    return Order(id=m.id, account_id=m.account_id, months=m.months, amount_uzs=m.amount_uzs, provider=m.provider,
                 status=m.status, created_at=m.created_at, paid_at=m.paid_at)


class DjangoOrderRepository(OrderRepository):
    def create(self, account_id: int, months: int, amount_uzs: int, provider: str) -> Order:
        return _order(OrderModel.objects.create(account_id=account_id, months=months, amount_uzs=amount_uzs, provider=provider))

    def get(self, order_id: int, for_update: bool = False) -> Order | None:
        qs = OrderModel.objects.filter(pk=order_id)
        m = (qs.select_for_update() if for_update else qs).first()
        return _order(m) if m else None

    def get_for_account(self, account_id: int, order_id: int) -> Order | None:
        m = OrderModel.objects.filter(pk=order_id, account_id=account_id).first()
        return _order(m) if m else None

    def set_status(self, order_id: int, status: str, paid: bool = False) -> None:
        fields = {"status": status}
        if paid:
            fields["paid_at"] = timezone.now()
        OrderModel.objects.filter(pk=order_id).update(**fields)


class ProviderPaymentLinks(PaymentLinks):
    def __init__(self, payme_cfg: dict, click_cfg: dict):
        self._payme, self._click = payme_cfg, click_cfg

    def payme(self, order: Order, return_url: str | None) -> str:
        params = f"m={self._payme['MERCHANT_ID']};ac.order_id={order.id};a={order.amount_uzs * 100}"
        if return_url:
            params += f";c={return_url}"
        return f"{self._payme['CHECKOUT_URL'].rstrip('/')}/{base64.b64encode(params.encode()).decode()}"

    def click(self, order: Order, return_url: str | None) -> str:
        q = {"service_id": self._click["SERVICE_ID"], "merchant_id": self._click["MERCHANT_ID"],
             "amount": order.amount_uzs, "transaction_param": order.id}
        if return_url:
            q["return_url"] = return_url
        return "https://my.click.uz/services/pay?" + urlencode(q)


class ClickMerchantInvoices(ClickInvoiceGateway):
    """Click Merchant API: https://docs.click.uz/en/?p=161 (invoice/create)."""

    def __init__(self, click_cfg: dict):
        self._cfg = click_cfg

    def create(self, order: Order, phone: str) -> int | None:
        ts = int(time.time())
        digest = hashlib.sha1(f"{ts}{self._cfg['SECRET_KEY']}".encode()).hexdigest()
        try:
            res = requests.post(
                "https://api.click.uz/v2/merchant/invoice/create",
                json={"service_id": int(self._cfg["SERVICE_ID"] or 0), "amount": order.amount_uzs,
                      "phone_number": phone, "merchant_trans_id": str(order.id)},
                headers={"Accept": "application/json", "Auth": f"{self._cfg['MERCHANT_USER_ID']}:{digest}:{ts}"},
                timeout=20,
            )
            data = res.json()
        except (requests.RequestException, ValueError) as exc:
            log.warning("Click invoice xatosi: %s", exc)
            raise ExternalServiceError("Click bilan bog'lanib bo'lmadi. Keyinroq urinib ko'ring.") from exc
        if data.get("error_code"):
            raise ExternalServiceError(data.get("error_note") or "Click hisobni qabul qilmadi.")
        return data.get("invoice_id")

    def remember(self, order: Order, phone: str, invoice_id: int | None) -> None:
        ClickInvoiceModel.objects.create(order_id=order.id, phone=phone, invoice_id=invoice_id)


def _payme(m: PaymeTransactionModel) -> PaymeTransaction:
    return PaymeTransaction(id=m.id, order_id=m.order_id, amount=m.amount, state=m.state, payme_time=m.payme_time,
                            create_time=m.create_time, perform_time=m.perform_time, cancel_time=m.cancel_time, reason=m.reason)


class DjangoPaymeStore(PaymeStore):
    def __init__(self, orders: OrderRepository, billing: BillingService):
        self._orders, self._billing = orders, billing

    def get_order(self, order_id):
        return self._orders.get(order_id)

    def get_tx(self, tx_id):
        m = PaymeTransactionModel.objects.filter(pk=tx_id).first()
        return _payme(m) if m else None

    def get_open_tx_for_order(self, order_id):
        m = PaymeTransactionModel.objects.filter(order_id=order_id, state__in=[1, 2]).first()
        return _payme(m) if m else None

    def insert_tx(self, tx):
        PaymeTransactionModel.objects.create(id=tx.id, order_id=tx.order_id, amount=tx.amount, state=tx.state,
                                             payme_time=tx.payme_time, create_time=tx.create_time)

    def update_tx(self, tx_id, **fields):
        PaymeTransactionModel.objects.filter(pk=tx_id).update(**fields)

    def activate_order(self, order_id):
        self._billing.activate_order(order_id)

    def revoke_order(self, order_id):
        self._billing.revoke_order(order_id)

    def list_tx(self, start, end):
        return [_payme(m) for m in PaymeTransactionModel.objects.filter(create_time__gte=start, create_time__lte=end).order_by("create_time")]


def _click(m: ClickTransactionModel) -> ClickTransaction:
    return ClickTransaction(id=m.id, click_trans_id=m.click_trans_id, order_id=m.order_id, amount=m.amount, status=m.status)


class DjangoClickStore(ClickStore):
    def __init__(self, orders: OrderRepository, billing: BillingService):
        self._orders, self._billing = orders, billing

    def get_order(self, order_id):
        return self._orders.get(order_id)

    def get_tx_by_click_id(self, click_trans_id):
        m = ClickTransactionModel.objects.filter(click_trans_id=click_trans_id).first()
        return _click(m) if m else None

    def get_tx(self, tx_id):
        m = ClickTransactionModel.objects.filter(pk=tx_id).first()
        return _click(m) if m else None

    def insert_tx(self, click_trans_id, order_id, amount: Decimal):
        return _click(ClickTransactionModel.objects.create(click_trans_id=click_trans_id, order_id=order_id, amount=amount, status="prepared"))

    def set_tx_status(self, tx_id, status):
        ClickTransactionModel.objects.filter(pk=tx_id).update(status=status)

    def activate_order(self, order_id):
        self._billing.activate_order(order_id)
