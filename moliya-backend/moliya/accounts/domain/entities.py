from dataclasses import dataclass
from datetime import datetime


@dataclass
class Account:
    """Telegram foydalanuvchisi. id = Telegram user id."""

    id: int
    first_name: str | None
    last_name: str | None
    username: str | None
    language_code: str | None
    chat_id: int | None
    created_at: datetime
    trial_ends_at: datetime
    paid_until: datetime | None
    last_reminder: str | None = None
    blocked_bot: bool = False
    phone: str | None = None
