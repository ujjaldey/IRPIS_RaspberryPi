from telegram import ParseMode
from telegram.ext import Defaults, Updater, CommandHandler

from app.bot.telegrambothelper import TelegramBotHelper
from app.util.common import Util


class TelegramBot(TelegramBotHelper):
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config
        self.mqtt_client = None
        self.display = None

        self.util = Util()

        defaults = Defaults(parse_mode=ParseMode.HTML)
        self.updater = Updater(token=config.get_telegram_api_key(), use_context=True, defaults=defaults,
                               request_kwargs={'read_timeout': 2, 'connect_timeout': 2})
        self.dp = self.updater.dispatcher

    def set_mqtt_client(self, mqtt_client):
        self.mqtt_client = mqtt_client

        if mqtt_client:
            self._greet_message()

    def set_display(self, display):
        self.display = display

    def add_handlers(self):
        self.dp.add_handler(CommandHandler('status', self._status))
        self.dp.add_handler(CommandHandler('wakeup', self._wakeup))
        self.dp.add_handler(CommandHandler('on', self._on))
        self.dp.add_handler(CommandHandler('off', self._off))

    def start(self):
        self.updater.start_polling()

    def send_response(self, message):
        self._send_response(message)
