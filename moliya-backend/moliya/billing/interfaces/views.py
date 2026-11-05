import time

from django.conf import settings
from django.db import transaction
from rest_framework import serializers, status
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from moliya.accounts.application.use_cases import access_for, serialize_access
from moliya.accounts.interfaces.authentication import SiteAuthentication
from moliya.accounts.interfaces.views import serialize_account
from moliya.billing.container import billing_service, click_store, payme_store, prices
from moliya.billing.domain import click, payme
from moliya.shared.domain.clock import utcnow


class OrderIn(serializers.Serializer):
    months = serializers.IntegerField(min_value=1)
    provider = serializers.ChoiceField(choices=("payme", "click"), default="payme")


class InvoiceIn(serializers.Serializer):
    months = serializers.IntegerField(min_value=1)
    phone = serializers.CharField(max_length=20)


def order_out(order) -> dict:
    return {"id": order.id, "months": order.months, "amount": order.amount_uzs, "provider": order.provider, "status": order.status}


class PricesView(APIView):
    authentication_classes: list = []
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({"prices": prices()})


class SiteMeView(APIView):
    """To'lov sayti: kirgan foydalanuvchi, obuna holati va narxlar."""

    authentication_classes = [SiteAuthentication]

    def get(self, request):
        account = request.user.account
        return Response({"account": serialize_account(account), "access": serialize_access(access_for(account, utcnow())), "prices": prices()})


class OrderCreateView(APIView):
    authentication_classes = [SiteAuthentication]

    def post(self, request):
        s = OrderIn(data=request.data)
        s.is_valid(raise_exception=True)
        order, url = billing_service().create_order(request.user.account, s.validated_data["months"], s.validated_data["provider"])
        return Response({"order": order_out(order), "payUrl": url}, status=status.HTTP_201_CREATED)


class InvoiceCreateView(APIView):
    authentication_classes = [SiteAuthentication]

    def post(self, request):
        s = InvoiceIn(data=request.data)
        s.is_valid(raise_exception=True)
        order, invoice_id = billing_service().send_click_invoice(request.user.account, s.validated_data["months"], s.validated_data["phone"])
        return Response({"order": order_out(order), "invoiceId": invoice_id}, status=status.HTTP_201_CREATED)


class OrderStatusView(APIView):
    authentication_classes = [SiteAuthentication]

    def get(self, request, order_id):
        account = request.user.account
        order = billing_service().order_status(account, order_id)
        fresh = billing_service().accounts.get(account.id)
        return Response({"order": order_out(order), "access": serialize_access(access_for(fresh, utcnow()))})


class PaymeWebhookView(APIView):
    """Payme Merchant API endpoint. Payme har doim HTTP 200 kutadi, xato JSON ichida."""

    authentication_classes: list = []
    permission_classes = [AllowAny]

    def post(self, request):
        with transaction.atomic():
            result = payme.process_request(payme_store(), request.headers.get("Authorization"), settings.PAYME["KEY"], request.body, int(time.time() * 1000))
        return Response(result)


class ClickWebhookView(APIView):
    """Click SHOP API: Prepare va Complete bitta manzilga keladi (action maydoni bilan ajratiladi)."""

    authentication_classes: list = []
    permission_classes = [AllowAny]
    parser_classes = [FormParser, MultiPartParser, JSONParser]

    def post(self, request):
        params = {k: str(v) for k, v in request.data.items()}
        with transaction.atomic():
            result = click.process(click_store(), params, settings.CLICK["SECRET_KEY"], settings.CLICK["SERVICE_ID"])
        return Response(result)
