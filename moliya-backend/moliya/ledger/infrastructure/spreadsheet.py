"""Excel hisobot (openpyxl): tanlangan oy, yil jamlanmasi, qarzlar va barcha yozuvlar."""
from datetime import date
from decimal import Decimal
from io import BytesIO

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter

from moliya.ledger.application.ports import DocumentSender, SpreadsheetBuilder
from moliya.ledger.domain.analytics import balance_before, month_of, totals
from moliya.ledger.domain.catalog import category_label, group_label, item_label
from moliya.ledger.domain.entities import Debt, LedgerSettings, Transaction
from moliya.shared.infrastructure.telegram.bot_client import TelegramBotClient

HEAD = Font(bold=True, color="FFFFFF")
FILL = PatternFill("solid", fgColor="1B2F5F")
T = {
    "uz": ["Sana", "Guruh", "Modda", "Toifa", "Izoh", "Usul", "Summa", "Valyuta", "So'mda", "Oy", "Tushum", "To'lovlar", "Xarajatlar", "Qarz to'lovlari", "Qoldiq", "Jamg'arma", "Qarz beruvchi", "Asl summa", "To'langan", "Qolgan", "Oylar", "Oylik to'lov", "To'lov sanasi", "Muddat", "Holat", "Barchasi", "Qarzlar"],
    "ru": ["Дата", "Группа", "Статья", "Категория", "Примечание", "Способ", "Сумма", "Валюта", "В сумах", "Месяц", "Доход", "Платежи", "Расходы", "Выплаты долгов", "Остаток", "Накопления", "Кредитор", "Сумма", "Выплачено", "Осталось", "Месяцев", "Ежемесячно", "Дата платежа", "Срок", "Статус", "Все", "Долги"],
    "en": ["Date", "Group", "Item", "Category", "Note", "Method", "Amount", "Currency", "In UZS", "Month", "Income", "Payments", "Expenses", "Debt payments", "Balance", "Savings", "Lender", "Original", "Paid", "Remaining", "Months", "Monthly", "Payment date", "Deadline", "Status", "All", "Debts"],
}
METHOD = {"cash": ("Naqd", "Наличные", "Cash"), "card": ("Karta", "Карта", "Card"), "bank": ("Bank o'tkazmasi", "Перечисление", "Bank transfer")}
STATUS = {"active": ("To'lanmoqda", "Выплачивается", "Repaying"), "paid": ("To'landi", "Оплачено", "Paid"), "overdue": ("Muddati o'tgan", "Просрочено", "Overdue")}
MONTHS = {
    "uz": ["Yanvar", "Fevral", "Mart", "Aprel", "May", "Iyun", "Iyul", "Avgust", "Sentabr", "Oktabr", "Noyabr", "Dekabr"],
    "ru": ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"],
    "en": ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
}


def _li(lang):
    return {"uz": 0, "ru": 1, "en": 2}.get(lang, 0)


def _sheet(wb, title, header, rows):
    ws = wb.create_sheet(title[:31])
    ws.append(header)
    for c in ws[1]:
        c.font, c.fill = HEAD, FILL
    for r in rows:
        ws.append([float(v) if isinstance(v, Decimal) else v for v in r])
    for i, _ in enumerate(header, 1):
        ws.column_dimensions[get_column_letter(i)].width = 18
    return ws


class OpenpyxlSpreadsheetBuilder(SpreadsheetBuilder):
    def build(self, *, month: str, lang: str, transactions: list[Transaction], debts: list[Debt], settings: LedgerSettings) -> bytes:
        lang = lang[:2] if lang and lang[:2] in T else "uz"
        t, li, rate = T[lang], _li(lang), settings.usd_rate
        wb = Workbook()
        wb.remove(wb.active)

        def tx_rows(items):
            for x in sorted(items, key=lambda x: (x.date, x.created_at or 0)):
                sign = 1 if x.type == "income" else -1
                yield [x.date.strftime("%d.%m.%Y"), group_label(x.group, lang), item_label(x.item, lang), category_label(x.category, lang),
                       x.note, METHOD.get(x.method, (x.method,) * 3)[li], x.amount, x.currency, sign * x.amount_uzs(rate)]

        tx_head = t[0:9]
        y, m = int(month[:4]), int(month[5:])
        _sheet(wb, f"{MONTHS[lang][m - 1]} {y}", tx_head, tx_rows([x for x in transactions if month_of(x) == month]))

        run = balance_before(transactions, f"{y:04d}-01", rate, settings.opening_balance)
        year_rows = []
        for mm in range(1, 13):
            key = f"{y:04d}-{mm:02d}"
            tot = totals([x for x in transactions if month_of(x) == key], rate)
            run += tot.net
            year_rows.append([MONTHS[lang][mm - 1], tot.inc, tot.pay, tot.exp, tot.debt, tot.net, run])
        _sheet(wb, str(y), [t[9], t[10], t[11], t[12], t[13], t[14], t[15]], year_rows)

        today = date.today()
        debt_rows = []
        for i, d in enumerate(debts, 1):
            s = d.summary(today)
            debt_rows.append([i, d.date.strftime("%d.%m.%Y") if d.date else "", d.lender, s.principal, s.paid, s.remaining, s.months,
                              s.monthly, d.pay_date.strftime("%d.%m.%Y") if d.pay_date else "",
                              d.deadline.strftime("%d.%m.%Y") if d.deadline else "", STATUS.get(s.status, (s.status,) * 3)[li], d.note])
        _sheet(wb, t[26], ["#", t[0], t[16], t[17], t[18], t[19], t[20], t[21], t[22], t[23], t[24], t[4]], debt_rows)
        _sheet(wb, t[25], tx_head, tx_rows(transactions))

        buf = BytesIO()
        wb.save(buf)
        return buf.getvalue()


class TelegramDocumentSender(DocumentSender):
    def __init__(self, client: TelegramBotClient):
        self._client = client

    def send(self, chat_id: int, filename: str, content: bytes, caption: str) -> bool:
        return bool(self._client.send_document(chat_id, filename, content, caption).get("ok"))
