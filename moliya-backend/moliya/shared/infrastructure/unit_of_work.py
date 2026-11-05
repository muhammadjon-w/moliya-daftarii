from django.db import transaction

from moliya.shared.application.unit_of_work import UnitOfWork


class DjangoUnitOfWork(UnitOfWork):
    def atomic(self):
        return transaction.atomic()
