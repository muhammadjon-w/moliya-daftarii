from abc import ABC, abstractmethod

from moliya.billing.domain.entities import Order


class OrderRepository(ABC):
    @abstractmethod
    def create(self, account_id: int, months: int, amount_uzs: int, provider: str) -> Order: ...

    @abstractmethod
    def get(self, order_id: int, for_update: bool = False) -> Order | None: ...

    @abstractmethod
    def get_for_account(self, account_id: int, order_id: int) -> Order | None: ...

    @abstractmethod
    def set_status(self, order_id: int, status: str, paid: bool = False) -> None: ...


class PaymentLinks(ABC):
    @abstractmethod
    def payme(self, order: Order, return_url: str | None) -> str: ...

    @abstractmethod
    def click(self, order: Order, return_url: str | None) -> str: ...


class ClickInvoiceGateway(ABC):
    @abstractmethod
    def create(self, order: Order, phone: str) -> int | None:
        """Hisob yaratadi va invoice_id qaytaradi. Xato bo'lsa ExternalServiceError chiqaradi."""

    @abstractmethod
    def remember(self, order: Order, phone: str, invoice_id: int | None) -> None: ...
