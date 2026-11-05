import hashlib
import hmac
import json
import time
from urllib.parse import urlencode

import pytest
from rest_framework.test import APIClient

BOT_TOKEN = "123456:TEST_TOKEN"


@pytest.fixture(autouse=True)
def _settings(settings):
    settings.TELEGRAM = {**settings.TELEGRAM, "BOT_TOKEN": BOT_TOKEN, "WEBHOOK_SECRET": "test-secret", "SITE_URL": "https://site.test"}
    settings.PAYME = {**settings.PAYME, "KEY": "payme-test-key", "MERCHANT_ID": "m1"}
    settings.CLICK = {**settings.CLICK, "SECRET_KEY": "click-secret", "SERVICE_ID": "77", "MERCHANT_ID": "9"}
    settings.TRIAL_DAYS = 30
    settings.DEV_AUTH_ENABLED = False


def make_init_data(user_id: int, first_name: str = "Ali", token: str = BOT_TOKEN, auth_date: int | None = None) -> str:
    fields = {"auth_date": str(auth_date or int(time.time())), "query_id": "AAE", "user": json.dumps({"id": user_id, "first_name": first_name})}
    check = "\n".join(f"{k}={fields[k]}" for k in sorted(fields))
    secret = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret, check.encode(), hashlib.sha256).hexdigest()
    return urlencode(fields)


def make_login(user_id: int, token: str = BOT_TOKEN) -> dict:
    data = {"id": user_id, "first_name": "Vali", "auth_date": int(time.time())}
    check = "\n".join(f"{k}={data[k]}" for k in sorted(data))
    data["hash"] = hmac.new(hashlib.sha256(token.encode()).digest(), check.encode(), hashlib.sha256).hexdigest()
    return data


@pytest.fixture
def client_for():
    def factory(user_id: int = 1001) -> APIClient:
        c = APIClient()
        c.credentials(HTTP_AUTHORIZATION="tma " + make_init_data(user_id))
        return c

    return factory


@pytest.fixture
def site_client():
    def factory(user_id: int = 1001) -> APIClient:
        c = APIClient()
        c.credentials(HTTP_X_TELEGRAM_LOGIN=json.dumps(make_login(user_id)))
        return c

    return factory


@pytest.fixture
def api() -> APIClient:
    return APIClient()
