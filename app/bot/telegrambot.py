from telegram import ParseMode
from telegram.ext import Defaults, Updater, CommandHandler

from app.bot.telegrambothelper import TelegramBotHelper


class TelegramBot(TelegramBotHelper):
    def __init__(self, config, logger, db, mqtt):
        self._set_logger(logger)
        self._set_config(config)
        self._set_db(db)
        self._set_mqtt(mqtt)

        defaults = Defaults(parse_mode=ParseMode.HTML)
        self.updater = Updater(token=config.get_telegram_api_key(), use_context=True, defaults=defaults)
        self.dp = self.updater.dispatcher

    def add_handlers(self):
        self.dp.add_handler(CommandHandler('status', self._status))
        # self.dp.add_handler(CommandHandler('help', self._help))
        # self.dp.add_handler(CallbackQueryHandler(self._detailed_help, pattern='^help_.*'))
        self.dp.add_handler(CommandHandler('on', self._on))
        self.dp.add_handler(CommandHandler('off', self._off))
        # self.dp.add_handler(CommandHandler('getdetail', self._get_detail))
        # self.dp.add_handler(CommandHandler('setalert', self._set_alert))
        # self.dp.add_handler(CommandHandler('getalerts', self._get_alerts))
        # self.dp.add_handler(CommandHandler('deletealert', self._delete_alert))
        # self.dp.add_handler(MessageHandler(Filters.regex(r'^.*$'), self._invalid_command))

    def start(self):
        self.updater.start_polling()
        self.updater.idle()
