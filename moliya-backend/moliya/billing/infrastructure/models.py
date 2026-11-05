from django.db import models

from moliya.accounts.infrastructure.models import AccountModel


class OrderModel(models.Model):
    STATUSES = [("new", "Yangi"), ("paid", "To'langan"), ("cancelled", "Bekor qilingan")]
    PROVIDERS = [("payme", "Payme"), ("click", "Click")]

    account = models.ForeignKey(AccountModel, on_delete=models.CASCADE, related_name="orders")
    months = models.PositiveIntegerField()
    amount_uzs = models.BigIntegerField()
    provider = models.CharField(max_length=10, choices=PROVIDERS, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUSES, default="new")
    created_at = models.DateTimeField(auto_now_add=True)
    paid_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        app_label = "billing"
        db_table = "orders"
        constraints = [models.CheckConstraint(condition=models.Q(amount_uzs__gt=0), name="order_amount_positive")]


class PaymeTransactionModel(models.Model):
    id = models.CharField(max_length=64, primary_key=True)
    order = models.ForeignKey(OrderModel, on_delete=models.PROTECT, related_name="payme_transactions")
    amount = models.BigIntegerField(help_text="tiyinda")
    state = models.IntegerField()
    payme_time = models.BigIntegerField(default=0)
    create_time = models.BigIntegerField()
    perform_time = models.BigIntegerField(default=0)
    cancel_time = models.BigIntegerField(default=0)
    reason = models.IntegerField(blank=True, null=True)

    class Meta:
        app_label = "billing"
        db_table = "payme_transactions"
        indexes = [models.Index(fields=["order"]), models.Index(fields=["create_time"])]


class ClickTransactionModel(models.Model):
    click_trans_id = models.BigIntegerField(unique=True)
    order = models.ForeignKey(OrderModel, on_delete=models.PROTECT, related_name="click_transactions")
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    status = models.CharField(max_length=12)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "billing"
        db_table = "click_transactions"


class ClickInvoiceModel(models.Model):
    order = models.ForeignKey(OrderModel, on_delete=models.PROTECT, related_name="click_invoices")
    invoice_id = models.BigIntegerField(blank=True, null=True)
    phone = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "billing"
        db_table = "click_invoices"
