from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from moliya.accounts.application.use_cases import serialize_access
from moliya.ledger.container import export_ledger, ledger_service
from moliya.ledger.interfaces.serializers import (
    DebtIn,
    DebtPaymentIn,
    ExportIn,
    PlanIn,
    SettingsIn,
    TransactionIn,
    debt_out,
    plans_out,
    settings_out,
    tx_out,
)


def _valid(serializer_cls, request, partial=False):
    s = serializer_cls(data=request.data, partial=partial)
    s.is_valid(raise_exception=True)
    return s


class StateView(APIView):
    """GET /api/v1/ledger/state — ilova ochilganda kerak bo'lgan hammasi bitta so'rovda."""

    def get(self, request):
        st = ledger_service().state(request.user.account)
        return Response({
            "access": serialize_access(st["access"]),
            "transactions": [tx_out(t) for t in st["transactions"]],
            "debts": [debt_out(d) for d in st["debts"]],
            "plans": plans_out(st["plans"]),
            "settings": settings_out(st["settings"]),
        })


class TransactionListView(APIView):
    def get(self, request):
        return Response([tx_out(t) for t in ledger_service().transactions.list(request.user.account.id)])

    def post(self, request):
        s = _valid(TransactionIn, request)
        tx = ledger_service().create_transaction(request.user.account, s.to_domain())
        return Response(tx_out(tx), status=status.HTTP_201_CREATED)


class TransactionDetailView(APIView):
    def put(self, request, tx_id):
        s = _valid(TransactionIn, request)
        return Response(tx_out(ledger_service().update_transaction(request.user.account, tx_id, s.to_domain())))

    def patch(self, request, tx_id):
        s = _valid(TransactionIn, request, partial=True)
        data = dict(s.validated_data)
        return Response(tx_out(ledger_service().update_transaction(request.user.account, tx_id, data)))

    def delete(self, request, tx_id):
        ledger_service().delete_transaction(request.user.account, tx_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DebtListView(APIView):
    def get(self, request):
        return Response([debt_out(d) for d in ledger_service().debts.list(request.user.account.id)])

    def post(self, request):
        s = _valid(DebtIn, request)
        return Response(debt_out(ledger_service().create_debt(request.user.account, s.to_domain())), status=status.HTTP_201_CREATED)


class DebtDetailView(APIView):
    def put(self, request, debt_id):
        s = _valid(DebtIn, request)
        return Response(debt_out(ledger_service().update_debt(request.user.account, debt_id, s.to_domain())))

    def delete(self, request, debt_id):
        ledger_service().delete_debt(request.user.account, debt_id)
        return Response(status=status.HTTP_204_NO_CONTENT)


class DebtPaymentView(APIView):
    """POST /api/v1/debts/<id>/payments — qarzga to'lov (xohlasa chiqimga ham yoziladi)."""

    def post(self, request, debt_id):
        s = _valid(DebtPaymentIn, request)
        v = s.validated_data
        debt, tx = ledger_service().record_debt_payment(request.user.account, debt_id, v["amount"], v["date"], v["logTransaction"])
        return Response({"debt": debt_out(debt), "transaction": tx_out(tx) if tx else None}, status=status.HTTP_201_CREATED)


class PlanListView(APIView):
    def get(self, request):
        return Response(plans_out(ledger_service().plans.list(request.user.account.id)))


class PlanDetailView(APIView):
    def put(self, request, month):
        s = _valid(PlanIn, request)
        plan = ledger_service().save_plan(request.user.account, month, s.validated_data["values"])
        return Response(plans_out([plan])[plan.month])


class PlanCopyView(APIView):
    def post(self, request, month):
        plan = ledger_service().copy_previous_plan(request.user.account, month)
        return Response(plans_out([plan])[plan.month])


class SettingsView(APIView):
    def get(self, request):
        return Response(settings_out(ledger_service().settings.get(request.user.account.id)))

    def put(self, request):
        s = _valid(SettingsIn, request)
        return Response(settings_out(ledger_service().update_settings(request.user.account, s.to_domain())))


class ExcelExportView(APIView):
    """POST /api/v1/exports/excel {month} — Excel fayl bot chatiga yuboriladi."""

    def post(self, request):
        s = _valid(ExportIn, request)
        filename = export_ledger().execute(request.user.account, s.validated_data["month"])
        return Response({"sent": True, "filename": filename})
