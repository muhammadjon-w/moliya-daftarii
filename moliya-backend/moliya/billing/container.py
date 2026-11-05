from django.conf import settings

from moliya.accounts.infrastructure.repositories import DjangoAccountRepository
from moliya.billing.application.use_cases import BillingService
from moliya.billing.domain.pricing import parse_prices
from moliya.billing.infrastructure.repositories import (
    ClickMerchantInvoices,
    DjangoClickStore,
    DjangoOrderRepository,
    DjangoPaymeStore,
    ProviderPaymentLinks,
)
from moliya.shared.infrastructure.unit_of_work import DjangoUnitOfWork


def prices() -> dict[str, int]:
    return parse_prices(settings.PRICES_JSON)


def billing_service() -> BillingService:
    return BillingService(
        DjangoOrderRepository(), DjangoAccountRepository(), ProviderPaymentLinks(settings.PAYME, settings.CLICK),
        ClickMerchantInvoices(settings.CLICK), DjangoUnitOfWork(), prices(), settings.TELEGRAM["SITE_URL"],
    )


def payme_store() -> DjangoPaymeStore:
    return DjangoPaymeStore(DjangoOrderRepository(), billing_service())


def click_store() -> DjangoClickStore:
    return DjangoClickStore(DjangoOrderRepository(), billing_service())
