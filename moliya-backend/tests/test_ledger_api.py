from datetime import timedelta

import pytest
from django.utils import timezone

from moliya.accounts.infrastructure.models import AccountModel

pytestmark = pytest.mark.django_db

TX = {"type": "expense", "item": "meals", "amount": "2600000", "currency": "UZS", "date": "2026-11-12", "method": "card", "note": "Bozor"}


def test_requires_telegram_auth(client):
    assert client.get("/api/v1/ledger/state").status_code in (401, 403)
    r = client.get("/api/v1/ledger/state", HTTP_AUTHORIZATION="tma user=bad&hash=x")
    assert r.status_code == 401 and r.json()["error"]


def test_state_creates_account_with_trial(client_for):
    r = client_for(1001).get("/api/v1/ledger/state")
    assert r.status_code == 200
    body = r.json()
    assert body["access"]["state"] == "trial" and body["access"]["daysLeft"] == 30
    assert body["transactions"] == [] and body["settings"] == {"usdRate": 12000.0, "openingBalance": 0.0}


def test_transaction_crud_and_isolation(client_for):
    me, other = client_for(1001), client_for(2002)
    created = me.post("/api/v1/transactions", TX, format="json")
    assert created.status_code == 201, created.content
    tx = created.json()
    assert (tx["category"], tx["group"], tx["amount"]) == ("food", "exp", 2600000.0)

    upd = me.put(f"/api/v1/transactions/{tx['id']}", {**TX, "amount": "3000000"}, format="json")
    assert upd.status_code == 200 and upd.json()["amount"] == 3000000.0
    patched = me.patch(f"/api/v1/transactions/{tx['id']}", {"note": "Korzinka"}, format="json")
    assert patched.json()["note"] == "Korzinka" and patched.json()["amount"] == 3000000.0

    # boshqa foydalanuvchi ko'rmaydi va o'zgartira olmaydi
    assert other.get("/api/v1/ledger/state").json()["transactions"] == []
    assert other.put(f"/api/v1/transactions/{tx['id']}", TX, format="json").status_code == 404
    assert other.delete(f"/api/v1/transactions/{tx['id']}").status_code == 404

    assert me.delete(f"/api/v1/transactions/{tx['id']}").status_code == 204
    assert me.get("/api/v1/ledger/state").json()["transactions"] == []


def test_validation_errors(client_for):
    me = client_for(1001)
    r = me.post("/api/v1/transactions", {**TX, "amount": "0"}, format="json")
    assert r.status_code == 400 and r.json()["error"] == "validation"
    assert me.post("/api/v1/transactions", {**TX, "currency": "EUR"}, format="json").status_code == 400


def test_expired_subscription_blocks_writes_but_allows_reads_and_deletes(client_for):
    me = client_for(1001)
    tx = me.post("/api/v1/transactions", TX, format="json").json()
    AccountModel.objects.filter(pk=1001).update(trial_ends_at=timezone.now() - timedelta(days=1))
    r = me.post("/api/v1/transactions", TX, format="json")
    assert r.status_code == 402 and r.json()["access"]["state"] == "expired"
    assert me.put(f"/api/v1/transactions/{tx['id']}", TX, format="json").status_code == 402
    assert me.get("/api/v1/ledger/state").status_code == 200
    assert me.delete(f"/api/v1/transactions/{tx['id']}").status_code == 204


def test_debts_and_payment_atomic(client_for):
    me = client_for(1001)
    d = me.post("/api/v1/debts", {"lender": "Dilshod", "principal": "10000000", "paid": "2000000", "months": 6, "payDate": "2026-11-10"}, format="json")
    assert d.status_code == 201, d.content
    debt = d.json()
    pay = me.post(f"/api/v1/debts/{debt['id']}/payments", {"amount": "1333333", "date": "2026-11-10"}, format="json")
    assert pay.status_code == 201
    assert pay.json()["debt"]["paid"] == 3333333.0
    assert pay.json()["transaction"]["group"] == "debt" and pay.json()["transaction"]["note"] == "Dilshod"
    no_log = me.post(f"/api/v1/debts/{debt['id']}/payments", {"amount": "1000", "date": "2026-11-11", "logTransaction": False}, format="json")
    assert no_log.json()["transaction"] is None
    state = me.get("/api/v1/ledger/state").json()
    assert len(state["transactions"]) == 1 and state["debts"][0]["paid"] == 3334333.0
    upd = me.put(f"/api/v1/debts/{debt['id']}", {"lender": "Dilshod aka", "principal": "10000000", "paid": "10000000"}, format="json")
    assert upd.json()["lender"] == "Dilshod aka"
    assert me.post(f"/api/v1/debts/{debt['id']}/payments", {"amount": "1", "date": "2026-11-11"}, format="json").status_code == 400
    assert me.delete(f"/api/v1/debts/{debt['id']}").status_code == 204


def test_plans_and_settings(client_for):
    me = client_for(1001)
    r = me.put("/api/v1/plans/2026-10", {"values": {"inc:salary": "20000000", "exp:food": "2000000"}}, format="json")
    assert r.status_code == 200 and r.json() == {"inc:salary": 20000000.0, "exp:food": 2000000.0}
    assert me.post("/api/v1/plans/2026-12/copy-previous").status_code == 404
    copied = me.post("/api/v1/plans/2026-11/copy-previous")
    assert copied.status_code == 200 and copied.json()["exp:food"] == 2000000.0
    assert set(me.get("/api/v1/plans").json()) == {"2026-10", "2026-11"}
    s = me.put("/api/v1/settings", {"usdRate": "12600", "openingBalance": "-500000"}, format="json")
    assert s.json() == {"usdRate": 12600.0, "openingBalance": -500000.0}


def test_excel_export_sends_document(client_for, monkeypatch):
    sent = {}

    def fake_send(self, chat_id, filename, content, caption=""):
        sent.update(chat_id=chat_id, filename=filename, size=len(content))
        return {"ok": True}

    monkeypatch.setattr("moliya.shared.infrastructure.telegram.bot_client.TelegramBotClient.send_document", fake_send)
    me = client_for(1001)
    me.post("/api/v1/transactions", TX, format="json")
    me.post("/api/v1/debts", {"lender": "A", "principal": "100"}, format="json")
    r = me.post("/api/v1/exports/excel", {"month": "2026-11"}, format="json")
    assert r.status_code == 200 and sent["chat_id"] == 1001 and sent["size"] > 1000

    monkeypatch.setattr("moliya.shared.infrastructure.telegram.bot_client.TelegramBotClient.send_document", lambda *a, **k: {"ok": False})
    assert me.post("/api/v1/exports/excel", {"month": "2026-11"}, format="json").status_code == 502


def test_me_endpoint(client_for):
    r = client_for(1001).get("/api/v1/me")
    assert r.status_code == 200 and r.json()["account"]["firstName"] == "Ali"
