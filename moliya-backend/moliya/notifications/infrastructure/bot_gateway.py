from moliya.notifications.application.ports import BotGateway
from moliya.shared.infrastructure.telegram.bot_client import TelegramBotClient


class TelegramBotGateway(BotGateway):
    def __init__(self, client: TelegramBotClient, mini_app_url: str):
        self._client, self._url = client, mini_app_url

    def send(self, chat_id: int, text: str, open_app_button: bool = False) -> dict:
        markup = None
        if open_app_button and self._url:
            markup = {"inline_keyboard": [[{"text": "📒 Daftarni ochish", "web_app": {"url": self._url}}]]}
        return self._client.send_message(chat_id, text, markup)
