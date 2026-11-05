import base64
import hashlib
from urllib.parse import urlencode
from datetime import timedelta

import pytest
from django.utils import timezone

from moliya.accounts.infrastructure.models import AccountModel
from moliya.billing.domain.click import expected_sign
from moliya.billing.infrastructure.models import OrderModel

pytestmark = pytest.mark.django_db
AUTH = "Basic " + base64.b64encode(b"Paycom:payme-test-key").decode()


def payme(client, method, params, auth=AUTH):
    return client.post("/api/v1/payments/payme", {"id": 1, "method": method, "params": params}, format="json", HTTP_AUTHORIZATION=auth).json()


def test_prices_public(api):
    assert api.get("/api/v1/billing/prices").json()["prices"]["1"] == 29000


def test_site_order_requires_login_widget(api, site_client):
    assert api.post("/api/v1/billing/orders", {"months": 1}, format="json").status_code in (401, 403)
    r = site_client(1001).post("/api/v1/billing/orders", {"months": 12, "provider": "payme"}, format="json")
    assert r.status_code == 201
    body = r.json()
    assert body["order"]["amount"] == 249000
    decoded = base64.b64decode(body["payUrl"].rsplit("/", 1)[1]).decode()
    assert f"ac.order_id={body['order']['id']}" in decoded and "a=24900000" in decoded
    assert site_client(1001).post("/api/v1/billing/orders", {"months": 2}, format="json").status_code == 400


def test_payme_full_flow_extends_subscription(api, site_client):
    order = site_client(1001).post("/api/v1/billing/orders", {"months": 1}, format="json").json()["order"]
    acc = AccountModel.objects.get(pk=1001)
    trial_end = acc.trial_ends_at
    params = {"amount": 2900000, "account": {"order_id": order["id"]}}

    assert payme(api, "CheckPerformTransaction", params, auth="Basic " + base64.b64encode(b"Paycom:wrong").decode())["error"]["code"] == -32504
    assert payme(api, "CheckPerformTransaction", {**params, "amount": 100})["error"]["code"] == -31001
    assert payme(api, "CheckPerformTransaction", params)["result"]["allow"] is True
    now_ms = int(timezone.now().timestamp() * 1000)
    created = payme(api, "CreateTransaction", {**params, "id": "pm-1", "time": now_ms})
    assert created["result"]["state"] == 1
    assert payme(api, "CreateTransaction", {**params, "id": "pm-2", "time": now_ms})["error"]["code"] == -31050
    done = payme(api, "PerformTransaction", {"id": "pm-1"})
    assert done["result"]["state"] == 2
    again = payme(api, "PerformTransaction", {"id": "pm-1"})
    assert again["result"]["perform_time"] == done["result"]["perform_time"]

    acc.refresh_from_db()
    assert OrderModel.objects.get(pk=order["id"]).status == "paid"
    # sinov paytida to'landi: obuna sinov tugaganidan boshlab 1 oy
    assert abs((acc.paid_until - trial_end) - timedelta(days=30)) <= timedelta(days=1)

    status = site_client(1001).get(f"/api/v1/billing/orders/{order['id']}").json()
    assert status["order"]["status"] == "paid" and status["access"]["state"] == "active"

    cancel = payme(api, "CancelTransaction", {"id": "pm-1", "reason": 5})
    assert cancel["result"]["state"] == -2
    acc.refresh_from_db()
    assert abs(acc.paid_until - trial_end) <= timedelta(days=1)
    assert payme(api, "CheckTransaction", {"id": "nope"})["error"]["code"] == -31003
    assert len(payme(api, "GetStatement", {"from": 0, "to": now_ms + 10_000})["result"]["transactions"]) == 1


def test_click_prepare_complete(api, site_client):
    order = site_client(1001).post("/api/v1/billing/orders", {"months": 1, "provider": "click"}, format="json").json()["order"]
    base = {"click_trans_id": "555", "service_id": "77", "click_paydoc_id": "1", "merchant_trans_id": str(order["id"]),
            "amount": "29000", "error": "0", "error_note": "", "sign_time": "2026-11-05 12:00:00"}

    def call(p, sign=None):
        body = urlencode({**p, "sign_string": sign or expected_sign(p, "click-secret")})
        return api.post("/api/v1/payments/click", body, content_type="application/x-www-form-urlencoded").json()

    assert call({**base, "action": "0"}, sign="x")["error"] == -1
    assert call({**base, "amount": "100", "action": "0"})["error"] == -2
    prep = call({**base, "action": "0"})
    assert prep["error"] == 0
    comp = call({**base, "action": "1", "merchant_prepare_id": str(prep["merchant_prepare_id"])})
    assert comp["error"] == 0
    assert OrderModel.objects.get(pk=order["id"]).status == "paid"
    assert call({**base, "action": "1", "merchant_prepare_id": str(prep["merchant_prepare_id"])})["error"] == -4
    assert AccountModel.objects.get(pk=1001).paid_until is not None


def test_click_invoice_validates_phone(site_client, monkeypatch):
    calls = {}

    def fake_create(self, order, phone):
        calls["phone"] = phone
        return 777

    monkeypatch.setattr("moliya.billing.infrastructure.repositories.ClickMerchantInvoices.create", fake_create)
    c = site_client(1001)
    assert c.post("/api/v1/billing/invoices", {"months": 1, "phone": "12345"}, format="json").status_code == 400
    r = c.post("/api/v1/billing/invoices", {"months": 1, "phone": "+998 90 123 45 67"}, format="json")
    assert r.status_code == 201 and r.json()["invoiceId"] == 777 and calls["phone"] == "998901234567"


def test_md5_signature_known():
    p = {"click_trans_id": "1", "service_id": "2", "merchant_trans_id": "3", "amount": "4", "action": "0", "sign_time": "t"}
    assert expected_sign(p, "s") == hashlib.md5(b"12s340t").hexdigest()
