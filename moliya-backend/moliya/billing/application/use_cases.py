"""Obuna sotish ssenariylari."""
import re

from moliya.accounts.application.ports import AccountRepository
from moliya.accounts.domain.access import extended_until, reduced_until
from moliya.accounts.domain.entities import Account
from moliya.billing.application.ports import ClickInvoiceGateway, OrderRepository, PaymentLinks
from moliya.billing.domain.entities import Order
from moliya.billing.domain.pricing import price_for
from moliya.shared.application.unit_of_work import UnitOfWork
from moliya.shared.domain.clock import utcnow
from moliya.shared.domain.errors import NotFound, ValidationFailed

PHONE_RE = re.compile(r"^998\d{9}$")


class BillingService:
    def __init__(self, orders: OrderRepository, accounts: AccountRepository, links: PaymentLinks, invoices: ClickInvoiceGateway,
                 uow: UnitOfWork, prices: dict[str, int], site_url: str = "", clock=utcnow):
        self.orders, self.accounts, self.links, self.invoices, self.uow = orders, accounts, links, invoices, uow
        self.prices, self.site_url, self._now = prices, site_url.rstrip("/"), clock

    def _plan(self, months) -> tuple[int, int]:
        try:
            months = int(months)
        except (TypeError, ValueError):
            months = 0
        amount = price_for(self.prices, months)
        if not amount:
            raise ValidationFailed("Bunday tarif yo'q.", field="months")
        return months, amount

    def _return_url(self, order: Order) -> str | None:
        return f"{self.site_url}/obuna?paid={order.id}" if self.site_url else None

    def create_order(self, account: Account, months, provider: str) -> tuple[Order, str]:
        if provider not in ("payme", "click"):
            raise ValidationFailed("To'lov tizimi noto'g'ri.", field="provider")
        months, amount = self._plan(months)
        order = self.orders.create(account.id, months, amount, provider)
        url = self.links.payme(order, self._return_url(order)) if provider == "payme" else self.links.click(order, self._return_url(order))
        return order, url

    def send_click_invoice(self, account: Account, months, phone: str) -> tuple[Order, int | None]:
        digits = re.sub(r"\D", "", phone or "")
        if len(digits) == 9:
            digits = "998" + digits
        if not PHONE_RE.match(digits):
            raise ValidationFailed("Telefon raqamni 998XXXXXXXXX ko'rinishida kiriting.", field="phone")
        months, amount = self._plan(months)
        order = self.orders.create(account.id, months, amount, "click")
        invoice_id = self.invoices.create(order, digits)
        self.invoices.remember(order, digits, invoice_id)
        self.accounts.set_phone(account.id, digits)
        return order, invoice_id

    def order_status(self, account: Account, order_id: int) -> Order:
        order = self.orders.get_for_account(account.id, order_id)
        if not order:
            raise NotFound("Buyurtma topilmadi.")
        return order

    # ---- to'lov tizimlari chaqiradi (takroriy chaqiruv xavfsiz) ----
    def activate_order(self, order_id: int) -> None:
        with self.uow.atomic():
            order = self.orders.get(order_id, for_update=True)
            if not order or order.status == "paid":
                return
            self.orders.set_status(order_id, "paid", paid=True)
            account = self.accounts.get_for_update(order.account_id)
            self.accounts.set_paid_until(account.id, extended_until(account.trial_ends_at, account.paid_until, order.months, self._now()))

    def revoke_order(self, order_id: int) -> None:
        with self.uow.atomic():
            order = self.orders.get(order_id, for_update=True)
            if not order:
                return
            if order.status != "paid":
                if order.status == "new":
                    self.orders.set_status(order_id, "cancelled")
                return
            self.orders.set_status(order_id, "cancelled")
            account = self.accounts.get_for_update(order.account_id)
            self.accounts.set_paid_until(account.id, reduced_until(account.paid_until, order.months))
