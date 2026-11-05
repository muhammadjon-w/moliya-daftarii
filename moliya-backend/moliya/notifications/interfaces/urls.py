from django.urls import path

from moliya.notifications.interfaces.views import TelegramWebhookView

urlpatterns = [path("telegram/webhook", TelegramWebhookView.as_view(), name="telegram-webhook")]
