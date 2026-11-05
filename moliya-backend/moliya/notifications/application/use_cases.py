import time

from moliya.accounts.application.ports import AccountRepository
from moliya.accounts.application.use_cases import access_for
from moliya.notifications.application.ports import BotGateway
from moliya.notifications.domain.reminders import pick_reminder
from moliya.shared.domain.clock import utcnow
from moliya.shared.infrastructure.telegram.signatures import TelegramIdentity


class HandleBotUpdate:
    """Bot webhook'iga kelgan xabarni qayta ishlaydi."""

    def __init__(self, accounts: AccountRepository, bot: BotGateway, trial_days: int, site_url: str = "", clock=utcnow):
        self._accounts, self._bot, self._trial_days, self._site, self._now = accounts, bot, trial_days, site_url, clock

    def execute(self, update: dict) -> None:
        member = update.get("my_chat_member")
        if member:
            blocked = (member.get("new_chat_member") or {}).get("status") == "kicked"
            self._accounts.set_blocked(member["from"]["id"], blocked)
            return
        msg = update.get("message") or {}
        sender, chat = msg.get("from"), msg.get("chat") or {}
        if not sender or chat.get("type") != "private":
            return
        identity = TelegramIdentity(id=sender["id"], first_name=sender.get("first_name"), last_name=sender.get("last_name"),
                                    username=sender.get("username"), language_code=sender.get("language_code"))
        account = self._accounts.upsert_from_identity(identity, self._trial_days, chat_id=chat["id"])
        access = access_for(account, self._now())
        text = (msg.get("text") or "").strip()
        fmt = lambda d: d.strftime("%d.%m.%Y")  # noqa: E731

        if text.startswith("/start"):
            status = (
                f"Sizda {access.days_left} kunlik bepul sinov muddati bor ({fmt(access.trial_ends_at)} gacha)." if access.state == "trial"
                else f"Obunangiz {fmt(access.paid_until)} gacha faol." if access.state == "active"
                else "Bepul sinov muddati tugagan. Yozuvlaringiz saqlangan, ularni ko'ra olasiz."
            )
            self._bot.send(chat["id"], f"Assalomu alaykum, {sender.get('first_name') or ''}!\n\n"
                                       f"Moliya daftari — tushum, chiqim, reja va qarzlaringizni so'm va dollarda yuritish uchun.\n\n{status}",
                           open_app_button=True)
        elif text.startswith("/obuna"):
            status = (
                f"Obuna faol: {fmt(access.paid_until)} gacha ({access.days_left} kun)." if access.state == "active"
                else f"Bepul sinov: {fmt(access.trial_ends_at)} gacha ({access.days_left} kun)." if access.state == "trial"
                else "Obuna faol emas."
            )
            site = f"\n\nObunani rasmiy saytimizda rasmiylashtirish mumkin: {self._site.rstrip('/')}/obuna" if self._site else ""
            self._bot.send(chat["id"], status + site)
        elif text.startswith("/yordam") or text.startswith("/help"):
            self._bot.send(chat["id"], "Buyruqlar:\n/start — daftarni ochish\n/obuna — obuna holati\n/yordam — yordam\n\nSavol bo'lsa, shu yerga yozing.")
        else:
            self._bot.send(chat["id"], "Daftarni ochish uchun quyidagi tugmani bosing.", open_app_button=True)


class SendReminders:
    def __init__(self, accounts: AccountRepository, bot: BotGateway, clock=utcnow, pause: float = 0.04):
        self._accounts, self._bot, self._now, self._pause = accounts, bot, clock, pause

    def execute(self) -> dict:
        now = self._now()
        candidates = self._accounts.reminder_candidates(now, horizon_days=6, past_days=2)
        sent = 0
        for acc in candidates:
            r = pick_reminder(acc.trial_ends_at, acc.paid_until, acc.last_reminder, now)
            if not r:
                continue
            res = self._bot.send(acc.chat_id, r.text, open_app_button=True)
            if res.get("ok"):
                sent += 1
                self._accounts.set_last_reminder(acc.id, r.key)
            elif res.get("error_code") == 403:
                self._accounts.set_blocked(acc.id, True)
            if self._pause:
                time.sleep(self._pause)  # Telegram limitlaridan oshmaslik uchun
        return {"checked": len(candidates), "sent": sent}
