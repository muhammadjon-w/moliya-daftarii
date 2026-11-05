"""Telegram imzolarini tekshirish.

- Mini app: https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app
- Login Widget: https://core.telegram.org/widgets/login#checking-authorization
"""
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from urllib.parse import parse_qsl


@dataclass(frozen=True)
class TelegramIdentity:
    id: int
    first_name: str | None = None
    last_name: str | None = None
    username: str | None = None
    language_code: str | None = None


def validate_init_data(init_data: str, bot_token: str, max_age: int = 86400, now: int | None = None) -> TelegramIdentity | None:
    if not init_data or not bot_token:
        return None
    pairs = dict(parse_qsl(init_data, keep_blank_values=True))
    received = pairs.pop("hash", None)
    if not received:
        return None
    check_string = "\n".join(f"{k}={pairs[k]}" for k in sorted(pairs))
    secret = hmac.new(b"WebAppData", bot_token.encode(), hashlib.sha256).digest()
    expected = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, received):
        return None
    auth_date = int(pairs.get("auth_date") or 0)
    if not auth_date or (now or int(time.time())) - auth_date > max_age:
        return None
    try:
        user = json.loads(pairs.get("user") or "null")
    except ValueError:
        return None
    if not isinstance(user, dict) or not isinstance(user.get("id"), int):
        return None
    return TelegramIdentity(
        id=user["id"],
        first_name=user.get("first_name"),
        last_name=user.get("last_name"),
        username=user.get("username"),
        language_code=user.get("language_code"),
    )


def validate_login_widget(data: dict, bot_token: str, max_age: int = 7 * 86400, now: int | None = None) -> TelegramIdentity | None:
    if not isinstance(data, dict) or not bot_token or not data.get("hash"):
        return None
    received = str(data["hash"])
    fields = {k: v for k, v in data.items() if k != "hash" and v not in (None, "")}
    check_string = "\n".join(f"{k}={fields[k]}" for k in sorted(fields))
    secret = hashlib.sha256(bot_token.encode()).digest()
    expected = hmac.new(secret, check_string.encode(), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, received):
        return None
    try:
        auth_date = int(fields.get("auth_date") or 0)
        user_id = int(fields["id"])
    except (KeyError, TypeError, ValueError):
        return None
    if not auth_date or (now or int(time.time())) - auth_date > max_age:
        return None
    return TelegramIdentity(
        id=user_id,
        first_name=fields.get("first_name"),
        last_name=fields.get("last_name"),
        username=fields.get("username"),
    )
