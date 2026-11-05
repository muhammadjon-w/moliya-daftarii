from datetime import timedelta

import pytest
from django.utils import timezone

from moliya.accounts.infrastructure.models import AccountModel
from moliya.notifications.container import send_reminders

pytestmark = pytest.mark.django_db


@pytest.fixture
def outbox(monkeypatch):
    sent = []

    def fake(self, chat_id, text, reply_markup=None):
        sent.append({"chat_id": chat_id, "text": text, "markup": reply_markup})
        return {"ok": True}

    monkeypatch.setattr("moliya.shared.infrastructure.telegram.bot_client.TelegramBotClient.send_message", fake)
    return sent


def update(text, uid=5005):
    return {"update_id": 1, "message": {"message_id": 1, "from": {"id": uid, "first_name": "Sardor", "language_code": "uz"},
                                        "chat": {"id": uid, "type": "private"}, "text": text}}


def test_webhook_rejects_wrong_secret(api, outbox):
    assert api.post("/api/v1/telegram/webhook", update("/start"), format="json").status_code == 403
    assert outbox == []


def test_start_creates_account_and_replies(api, outbox, settings):
    settings.TELEGRAM = {**settings.TELEGRAM, "MINI_APP_URL": "https://app.test/"}
    r = api.post("/api/v1/telegram/webhook", update("/start"), format="json", HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN="test-secret")
    assert r.status_code == 200
    acc = AccountModel.objects.get(pk=5005)
    assert acc.chat_id == 5005 and acc.first_name == "Sardor"
    assert "30 kunlik bepul sinov" in outbox[0]["text"]
    assert outbox[0]["markup"]["inline_keyboard"][0][0]["web_app"]["url"] == "https://app.test/"
    api.post("/api/v1/telegram/webhook", update("/obuna"), format="json", HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN="test-secret")
    assert "Bepul sinov" in outbox[1]["text"] and "https://site.test" in outbox[1]["text"]


def test_block_and_reminders(api, outbox):
    api.post("/api/v1/telegram/webhook", update("/start"), format="json", HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN="test-secret")
    AccountModel.objects.filter(pk=5005).update(trial_ends_at=timezone.now() + timedelta(days=3))
    outbox.clear()
    svc = send_reminders()
    svc._pause = 0
    assert svc.execute() == {"checked": 1, "sent": 1}
    assert "Bepul sinov muddati" in outbox[0]["text"]
    assert svc.execute()["sent"] == 0  # bir marta yuboriladi
    api.post("/api/v1/telegram/webhook", {"my_chat_member": {"from": {"id": 5005}, "new_chat_member": {"status": "kicked"}}},
                format="json", HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN="test-secret")
    assert AccountModel.objects.get(pk=5005).blocked_bot is True
