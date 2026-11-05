from datetime import date, datetime, timezone
from decimal import Decimal

import pytest

from moliya.accounts.domain.access import access_of, extended_until, reduced_until
from moliya.ledger.domain.entities import Debt, LedgerSettings, MonthPlan, Transaction
from moliya.notifications.domain.reminders import pick_reminder
from moliya.shared.domain.clock import add_months
from moliya.shared.domain.errors import ValidationFailed
from moliya.shared.infrastructure.telegram.signatures import validate_init_data, validate_login_widget
from tests.conftest import BOT_TOKEN, make_init_data, make_login


def dt(s):
    return datetime.fromisoformat(s).replace(tzinfo=timezone.utc)


def test_add_months_clamps_end_of_month():
    assert add_months(dt("2026-01-31T10:00:00"), 1) == dt("2026-02-28T10:00:00")
    assert add_months(dt("2026-11-15T00:00:00"), 3) == dt("2027-02-15T00:00:00")
    assert add_months(dt("2026-03-31T00:00:00"), -1) == dt("2026-02-28T00:00:00")


def test_access_states_and_extension():
    now = dt("2026-11-10T00:00:00")
    assert access_of(dt("2026-11-20T00:00:00"), None, now).state == "trial"
    assert access_of(dt("2026-11-01T00:00:00"), None, now).can_write is False
    a = access_of(dt("2026-11-01T00:00:00"), dt("2026-12-10T00:00:00"), now)
    assert (a.state, a.days_left) == ("active", 30)
    # sinov paytida to'lansa, sinov tugaganidan boshlab hisoblanadi
    assert extended_until(dt("2026-11-20T00:00:00"), None, 1, now) == dt("2026-12-20T00:00:00")
    assert reduced_until(dt("2026-12-20T00:00:00"), 1) == dt("2026-11-20T00:00:00")


def test_transaction_rules():
    tx = Transaction(account_id=1, type="expense", group="exp", item="rent", category="", amount="4500000", currency="UZS", date=date(2026, 11, 3), method="bank")
    assert (tx.category, tx.group, tx.amount) == ("housing", "pay", Decimal("4500000.00"))
    inc = Transaction(account_id=1, type="income", group="exp", item="salary", category="", amount=1, currency="USD", date=date(2026, 11, 3), method="card")
    assert inc.group == "inc" and inc.amount_uzs(Decimal("12600")) == Decimal("12600.00")
    custom = Transaction(account_id=1, type="expense", group="debt", item="Ota-onamga", category="", amount=5, currency="UZS", date=date(2026, 11, 3), method="cash")
    assert custom.category == "Ota-onamga" and custom.group == "debt"
    for bad in ({"amount": 0}, {"currency": "EUR"}, {"method": "crypto"}, {"item": "  "}, {"type": "x"}):
        base = dict(account_id=1, type="expense", group="exp", item="meals", category="", amount=1, currency="UZS", date=date(2026, 1, 1), method="cash")
        with pytest.raises(ValidationFailed):
            Transaction(**{**base, **bad})


def test_debt_summary_and_payment():
    d = Debt(account_id=1, lender="Dilshod", principal="10000000", paid="2000000", months=6, deadline=date(2026, 10, 1))
    s = d.summary(date(2026, 11, 5))
    assert (s.remaining, s.monthly, s.status) == (Decimal("8000000.00"), Decimal("1333333.33"), "overdue")
    paid = d.with_payment("8000000")
    assert paid.summary(date(2026, 11, 5)).status == "paid"


def test_debt_installment_moves_schedule():
    d = Debt(account_id=1, lender="Bank", principal="12000000", months=12, pay_date=date(2027, 1, 31))
    # to'liq oylik to'lov: qolgan oylar −1, sana +1 oy (oy oxiri to'g'ri), oylik to'lov o'zgarmaydi
    after = d.with_payment("1000000")
    assert (after.months, after.pay_date) == (11, date(2027, 2, 28))
    assert after.summary(date(2027, 1, 1)).monthly == Decimal("1000000.00")
    # qisman to'lov: jadval o'zgarmaydi
    partial = d.with_payment("400000")
    assert (partial.months, partial.pay_date) == (12, date(2027, 1, 31))
    # to'liq yopilsa: jadval o'zgarmaydi, holat "paid"
    closed = d.with_payment("12000000")
    assert (closed.months, closed.pay_date) == (12, date(2027, 1, 31))
    assert closed.summary(date(2027, 1, 1)).status == "paid"


def test_plan_and_settings_validation():
    p = MonthPlan(month="2026-11", values={"inc:salary": "20000000", "exp:food": 0})
    assert p.values == {"inc:salary": Decimal("20000000.00")}
    with pytest.raises(ValidationFailed):
        MonthPlan(month="2026-13", values={})
    with pytest.raises(ValidationFailed):
        MonthPlan(month="2026-11", values={"bad key!": 1})
    with pytest.raises(ValidationFailed):
        LedgerSettings(usd_rate=0)


def test_reminder_rules():
    now = dt("2026-11-10T09:00:00")
    assert pick_reminder(dt("2026-11-13T00:00:00"), None, None, now).key == "trial_5"
    assert pick_reminder(dt("2026-11-13T00:00:00"), None, "trial_5", now) is None
    assert pick_reminder(dt("2026-11-09T12:00:00"), None, "trial_5", now).key == "trial_0"
    assert pick_reminder(dt("2026-10-01T00:00:00"), dt("2026-11-12T00:00:00"), "trial_0", now).key == "paid_3:2026-11-12"
    assert pick_reminder(dt("2026-10-01T00:00:00"), dt("2026-12-12T00:00:00"), None, now) is None


def test_telegram_signatures():
    init = make_init_data(42)
    assert validate_init_data(init, BOT_TOKEN).id == 42
    assert validate_init_data(init.replace("Ali", "Bob"), BOT_TOKEN) is None
    assert validate_init_data(init, "other:token") is None
    assert validate_init_data(make_init_data(42, auth_date=1), BOT_TOKEN) is None
    login = make_login(7)
    assert validate_login_widget(login, BOT_TOKEN).id == 7
    assert validate_login_widget({**login, "id": 8}, BOT_TOKEN) is None
