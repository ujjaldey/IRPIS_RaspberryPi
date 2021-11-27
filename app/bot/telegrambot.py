from time import time

from telegram import ParseMode
from telegram.ext import Defaults, Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters

from app.bot.telegrambothelper import TelegramBotHelper
from app.util.common import Common


class TelegramBot(TelegramBotHelper):
    def __init__(self, logger, config, db, app_start_time):
        self.logger = logger
        self.config = config
        self.db = db
        self.app_start_time = app_start_time if app_start_time > 0 else time()
        self.conn = db.connect().execution_options(autocommit=True)

        self.mqtt_client = None
        self.display = None

        self.common = Common()

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
        self.dp.add_handler(CommandHandler('help', self._help))
        self.dp.add_handler(CallbackQueryHandler(self._detailed_help, pattern='^help_.*'))
        self.dp.add_handler(CommandHandler('status', self._status))
        self.dp.add_handler(CommandHandler('wakeup', self._wakeup))
        self.dp.add_handler(CommandHandler('on', self._on))
        self.dp.add_handler(CommandHandler('off', self._off))
        self.dp.add_handler(CommandHandler('next', self._next))
        self.dp.add_handler(CommandHandler('last', self._last))
        self.dp.add_handler(CommandHandler('skip', self._skip))
        self.dp.add_handler(CommandHandler('history', self._history))
        self.dp.add_handler(CommandHandler('schedule', self._schedule))
        self.dp.add_handler(CommandHandler('reboot', self._reboot_confirm))
        self.dp.add_handler(CallbackQueryHandler(self._reboot, pattern='^reboot_.*'))
        self.dp.add_handler(CommandHandler('shutdown', self._shutdown_confirm))
        self.dp.add_handler(CallbackQueryHandler(self._shutdown, pattern='^shutdown_.*'))
        self.dp.add_handler(MessageHandler(Filters.regex(r'^.*$'), self._invalid_command))

    def start(self):
        self.updater.start_polling()

    def send_response(self, message):
        self._send_response(message)
