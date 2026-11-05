"""Vaqt bilan ishlash uchun sof yordamchilar."""
import calendar
from datetime import date, datetime, timezone


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def add_months(value: datetime, months: int) -> datetime:
    """Sanaga oy qo'shadi (manfiy bo'lsa ayiradi), oy oxirini to'g'ri hisoblaydi: 31-yanvar + 1 oy = 28/29-fevral."""
    total = value.month - 1 + months
    year, month = value.year + total // 12, total % 12 + 1
    day = min(value.day, calendar.monthrange(year, month)[1])
    return value.replace(year=year, month=month, day=day)


def month_key(d: date) -> str:
    return f"{d.year:04d}-{d.month:02d}"
