from django.urls import path, re_path

from moliya.ledger.interfaces import views

MONTH = r"(?P<month>\d{4}-\d{2})"

urlpatterns = [
    path("ledger/state", views.StateView.as_view(), name="ledger-state"),
    path("transactions", views.TransactionListView.as_view(), name="transactions"),
    path("transactions/<uuid:tx_id>", views.TransactionDetailView.as_view(), name="transaction-detail"),
    path("debts", views.DebtListView.as_view(), name="debts"),
    path("debts/<uuid:debt_id>", views.DebtDetailView.as_view(), name="debt-detail"),
    path("debts/<uuid:debt_id>/payments", views.DebtPaymentView.as_view(), name="debt-payments"),
    path("plans", views.PlanListView.as_view(), name="plans"),
    re_path(rf"^plans/{MONTH}$", views.PlanDetailView.as_view(), name="plan-detail"),
    re_path(rf"^plans/{MONTH}/copy-previous$", views.PlanCopyView.as_view(), name="plan-copy"),
    path("settings", views.SettingsView.as_view(), name="settings"),
    path("exports/excel", views.ExcelExportView.as_view(), name="export-excel"),
]
