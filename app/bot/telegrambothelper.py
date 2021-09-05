from telegram import Update
from telegram.ext import CallbackContext


class TelegramBotHelper:
    def _set_logger(self, logger):
        self.logger = logger

    def _set_config(self, config):
        self.config = config

    def _set_db(self, db):
        self.db = db
        # self.conn = db.connect()

    def _set_mqtt(self, mqtt):
        self.mqtt = mqtt

    def _status(self, update: Update, context: CallbackContext):
        self.logger.info('_status is called')

        response_msg = 'ℹ <b><i>@{bot_name}</i></b> is up and running\n\n' \
                       'Try /help for help'.format(bot_name=self.config.get_telegram_bot_name())

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)

    def _on(self, update: Update, context: CallbackContext):
        self.logger.info('_on is called')

        response_msg = 'OK. Turning the irrigation on...'
        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)

        self.mqtt.publish("irpis/esp8266/command", "{\"sender\": \"IRPIS-RPI\", \"action\": \"ON\", \"duration\": 20}")

    def _off(self, update: Update, context: CallbackContext):
        self.logger.info('_off is called')

        response_msg = 'OK. Turning the irrigation off...'
        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)

        self.mqtt.publish("irpis/esp8266/command", "{\"sender\": \"IRPIS-RPI\", \"action\": \"OFF\"}")
