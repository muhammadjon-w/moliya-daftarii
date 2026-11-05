import uuid

from django.db import models

from moliya.accounts.infrastructure.models import AccountModel


class TransactionModel(models.Model):
    TYPES = [("income", "Tushum"), ("expense", "Chiqim")]
    GROUPS = [("inc", "Tushum"), ("pay", "To'lov"), ("exp", "Xarajat"), ("debt", "Qarz to'lovi")]
    CURRENCIES = [("UZS", "So'm"), ("USD", "Dollar")]
    METHODS = [("cash", "Naqd"), ("card", "Karta"), ("bank", "Bank o'tkazmasi")]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(AccountModel, on_delete=models.CASCADE, related_name="transactions")
    type = models.CharField(max_length=10, choices=TYPES)
    group = models.CharField(max_length=10, choices=GROUPS)
    item = models.CharField(max_length=120)
    category = models.CharField(max_length=120)
    amount = models.DecimalField(max_digits=18, decimal_places=2)
    currency = models.CharField(max_length=3, choices=CURRENCIES, default="UZS")
    date = models.DateField()
    method = models.CharField(max_length=10, choices=METHODS, default="cash")
    note = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "ledger"
        db_table = "transactions"
        ordering = ["date", "created_at"]
        indexes = [models.Index(fields=["account", "date"])]
        constraints = [models.CheckConstraint(condition=models.Q(amount__gt=0), name="transaction_amount_positive")]


class DebtModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    account = models.ForeignKey(AccountModel, on_delete=models.CASCADE, related_name="debts")
    lender = models.CharField(max_length=200, blank=True, default="")
    principal = models.DecimalField(max_digits=18, decimal_places=2)
    paid = models.DecimalField(max_digits=18, decimal_places=2, default=0)
    months = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=10, blank=True, default="")
    date = models.DateField(blank=True, null=True)
    pay_date = models.DateField(blank=True, null=True)
    deadline = models.DateField(blank=True, null=True)
    note = models.TextField(blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        app_label = "ledger"
        db_table = "debts"
        ordering = ["created_at"]
        indexes = [models.Index(fields=["account"])]


class PlanModel(models.Model):
    account = models.ForeignKey(AccountModel, on_delete=models.CASCADE, related_name="plans")
    month = models.CharField(max_length=7)
    values = models.JSONField(default=dict)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = "ledger"
        db_table = "plans"
        constraints = [models.UniqueConstraint(fields=["account", "month"], name="plan_unique_month")]


class SettingsModel(models.Model):
    account = models.OneToOneField(AccountModel, on_delete=models.CASCADE, primary_key=True, related_name="ledger_settings")
    usd_rate = models.DecimalField(max_digits=18, decimal_places=2, default=12000)
    opening_balance = models.DecimalField(max_digits=18, decimal_places=2, default=0)

    class Meta:
        app_label = "ledger"
        db_table = "ledger_settings"
