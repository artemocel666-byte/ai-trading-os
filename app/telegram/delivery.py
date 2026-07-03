from telegram import Bot

from app.core.enums import MessageType
from app.telegram.formatter import TelegramFormatter


class TelegramDelivery:
    def __init__(self, bot: Bot, formatter: TelegramFormatter) -> None:
        self._bot = bot
        self._formatter = formatter

    async def send(self, chat_id: int, message_type: MessageType, body_ru: str) -> None:
        message = self._formatter.format(message_type, body_ru)
        await self._bot.send_message(chat_id=chat_id, text=message)
