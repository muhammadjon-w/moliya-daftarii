from abc import ABC, abstractmethod


class BotGateway(ABC):
    @abstractmethod
    def send(self, chat_id: int, text: str, open_app_button: bool = False) -> dict:
        """Xabar yuboradi. Natija: {"ok": bool, "error_code"?: int}."""
