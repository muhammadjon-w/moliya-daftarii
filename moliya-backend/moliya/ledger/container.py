"""Bog'lovchi (composition root): portlarni Django amalga oshirishlari bilan ulaydi."""
from django.conf import settings

from moliya.ledger.application.use_cases import ExportLedger, LedgerService
from moliya.ledger.infrastructure.repositories import (
    DjangoDebtRepository,
    DjangoPlanRepository,
    DjangoSettingsRepository,
    DjangoTransactionRepository,
)
from moliya.ledger.infrastructure.spreadsheet import OpenpyxlSpreadsheetBuilder, TelegramDocumentSender
from moliya.shared.infrastructure.telegram.bot_client import TelegramBotClient
from moliya.shared.infrastructure.unit_of_work import DjangoUnitOfWork


def ledger_service() -> LedgerService:
    return LedgerService(
        DjangoTransactionRepository(), DjangoDebtRepository(), DjangoPlanRepository(), DjangoSettingsRepository(), DjangoUnitOfWork()
    )


def export_ledger() -> ExportLedger:
    return ExportLedger(ledger_service(), OpenpyxlSpreadsheetBuilder(), TelegramDocumentSender(TelegramBotClient(settings.TELEGRAM["BOT_TOKEN"])))
