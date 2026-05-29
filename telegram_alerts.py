from telegram import Bot
import ssl
import certifi

ssl_context = ssl.create_default_context(
    cafile=certifi.where()
)

class TelegramAlerts:

    def __init__(
        self,
        token,
        chat_id
    ):

        self.bot = Bot(token)

        self.chat_id = chat_id

    async def send(
        self,
        message
    ):

        await self.bot.send_message(
            chat_id=self.chat_id,
            text=message
        )