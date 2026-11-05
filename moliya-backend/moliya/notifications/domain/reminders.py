"""Qaysi eslatma yuborilishini aniqlaydi (sof funksiya)."""
from dataclasses import dataclass
from datetime import datetime

DAY = 86400


@dataclass(frozen=True)
class Reminder:
    key: str
    text: str


def _fmt(d: datetime) -> str:
    return d.strftime("%d.%m.%Y")


def pick_reminder(trial_ends_at: datetime, paid_until: datetime | None, last_reminder: str | None, now: datetime) -> Reminder | None:
    if paid_until and paid_until > now:
        left = (paid_until - now).total_seconds() / DAY
        key = f"paid_3:{paid_until.date().isoformat()}"
        if left <= 3 and last_reminder != key:
            return Reminder(key, f"Obunangiz {_fmt(paid_until)} da tugaydi. Yozuvlaringiz to'xtovsiz davom etishi uchun /obuna buyrug'ini yuboring.")
        return None
    left = (trial_ends_at - now).total_seconds() / DAY
    if 0 < left <= 5 and not (last_reminder or "").startswith("trial_"):
        return Reminder("trial_5", f"Bepul sinov muddati {_fmt(trial_ends_at)} da tugaydi. Batafsil: /obuna")
    if -2 < left <= 0 and last_reminder != "trial_0":
        return Reminder("trial_0", "Bepul sinov muddati tugadi. Yozuvlaringiz saqlangan va ularni ko'ra olasiz. Yangi yozuv qo'shish uchun: /obuna")
    return None
