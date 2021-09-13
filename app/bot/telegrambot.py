from telegram import ParseMode
from telegram.ext import Defaults, Updater, CommandHandler

from app.bot.telegrambothelper import TelegramBotHelper


class TelegramBot(TelegramBotHelper):
    def __init__(self, config, logger, db=None):
        self._set_logger(logger)
        self._set_config(config)
        self._set_db(db)

        defaults = Defaults(parse_mode=ParseMode.HTML)
        self.updater = Updater(token=config.get_telegram_api_key(), use_context=True, defaults=defaults,
                               request_kwargs={'read_timeout': 2, 'connect_timeout': 2})
        self.dp = self.updater.dispatcher

    def set_mqtt(self, mqtt):
        self._set_mqtt(mqtt)

        if mqtt:
            self._greet_message()

    def add_handlers(self):
        self.dp.add_handler(CommandHandler('status', self._status))
        self.dp.add_handler(CommandHandler('on', self._on))
        self.dp.add_handler(CommandHandler('off', self._off))

    def start(self):
        self.updater.start_polling()

    def send_response(self, message):
        self._send_response(message)
