"""Telegram Bot API bilan ishlovchi oddiy mijoz."""
import logging

import requests

log = logging.getLogger(__name__)


class TelegramBotClient:
    def __init__(self, token: str, timeout: float = 15.0):
        self._token = token
        self._timeout = timeout

    def _url(self, method: str) -> str:
        return f"https://api.telegram.org/bot{self._token}/{method}"

    def call(self, method: str, payload: dict) -> dict:
        if not self._token:
            return {"ok": False, "description": "BOT_TOKEN sozlanmagan"}
        try:
            res = requests.post(self._url(method), json=payload, timeout=self._timeout)
            return res.json()
        except (requests.RequestException, ValueError) as exc:
            log.warning("Telegram %s xatosi: %s", method, exc)
            return {"ok": False, "description": str(exc)}

    def send_message(self, chat_id: int, text: str, reply_markup: dict | None = None) -> dict:
        payload = {"chat_id": chat_id, "text": text, "disable_web_page_preview": True}
        if reply_markup:
            payload["reply_markup"] = reply_markup
        return self.call("sendMessage", payload)

    def send_document(self, chat_id: int, filename: str, content: bytes, caption: str = "") -> dict:
        if not self._token:
            return {"ok": False, "description": "BOT_TOKEN sozlanmagan"}
        try:
            res = requests.post(
                self._url("sendDocument"),
                data={"chat_id": chat_id, "caption": caption},
                files={"document": (filename, content)},
                timeout=self._timeout * 2,
            )
            return res.json()
        except (requests.RequestException, ValueError) as exc:
            log.warning("Telegram sendDocument xatosi: %s", exc)
            return {"ok": False, "description": str(exc)}
