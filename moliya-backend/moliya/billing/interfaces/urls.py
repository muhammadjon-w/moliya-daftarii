from django.urls import path

from moliya.billing.interfaces import views

urlpatterns = [
    path("billing/prices", views.PricesView.as_view(), name="billing-prices"),
    path("billing/me", views.SiteMeView.as_view(), name="billing-me"),
    path("billing/orders", views.OrderCreateView.as_view(), name="billing-orders"),
    path("billing/orders/<int:order_id>", views.OrderStatusView.as_view(), name="billing-order"),
    path("billing/invoices", views.InvoiceCreateView.as_view(), name="billing-invoices"),
    path("payments/payme", views.PaymeWebhookView.as_view(), name="payme-webhook"),
    path("payments/click", views.ClickWebhookView.as_view(), name="click-webhook"),
]
