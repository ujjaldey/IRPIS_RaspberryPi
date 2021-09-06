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

    def _greet_message(self):
        self.updater.bot.send_message(chat_id=self.config.get_telegram_chat_id(),
                                      text='<b><i>IOT Remote Plant Irrigation System (IRPIS)</i></b> initiating...')

    def _status(self, update: Update, context: CallbackContext):
        self.logger.info('_status is called')

        response_msg = 'ℹ <b><i>@{bot_name}</i></b> is up and running\n\n' \
                       'Try /help for help'.format(bot_name=self.config.get_telegram_bot_name())

        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)

    def _on(self, update: Update, context: CallbackContext):
        self.logger.info('_on is called')

        if len(context.args) < 1:
            response_msg = 'Enter the duration!'
            success = False
        else:
            duration_str = context.args[0]

            if len(context.args) > 1:
                duration_str = context.args[0] + context.args[1]

            duration = self.__convert_duration_to_secs(duration_str.lower())
            print(duration)

            if duration > 0:
                response_msg = f'OK. Turning the irrigation on for {self.__convert_secs_to_human_format(duration)}...'
                success = True
            else:
                response_msg = 'Invalid duration!'
                success = False

        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)

        if success:
            self.mqtt.publish(self.config.get_mqtt_command_topic(),
                              f'{{\"sender\": \"IRPIS-RPI\", \"action\": \"ON\", \"duration\": {duration}}}')

    def _off(self, update: Update, context: CallbackContext):
        self.logger.info('_off is called')

        response_msg = 'OK. Turning the irrigation off...'
        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)

        self.mqtt.publish(self.config.get_mqtt_command_topic(), '{\"sender\": \"IRPIS-RPI\", \"action\": \"OFF\"}')

    def _send_response(self, message):
        self.updater.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=message)

    @staticmethod
    def __convert_duration_to_secs(duration_str):
        count = duration_str.count(':')

        if count == 0:
            m = int(duration_str) if duration_str.isnumeric() else 0
            duration = m * 60
        elif count == 1:
            m_str = duration_str.split(":")[0]
            s_str = duration_str.split(":")[1]
            m = int(m_str) if m_str.isnumeric() else 0
            s = int(s_str) if s_str.isnumeric() else 0
            duration = m * 60 + s
        elif count == 2:
            h_str = duration_str.split(":")[0]
            m_str = duration_str.split(":")[1]
            s_str = duration_str.split(":")[2]
            h = int(h_str) if h_str.isnumeric() else 0
            m = int(m_str) if m_str.isnumeric() else 0
            s = int(s_str) if s_str.isnumeric() else 0
            duration = h * 3600 + m * 60 + s
        else:
            duration = -1

        return duration

    @staticmethod
    def __convert_secs_to_human_format(seconds):
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)

        return ((str(h) + ' hr ' if h > 0 else '') +
                (str(m) + ' min ' if m > 0 else '') +
                (str(s) + ' sec ' if s > 0 else '')).strip()
