import re
from datetime import datetime

from dateutil import parser
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
            # duration_str = context.args[0]
            #
            # if len(context.args) > 1:
            #     duration_str = context.args[0] + context.args[1]

            try:
                duration_str = " ".join(context.args)
                print(duration_str)

                duration = self.__convert_duration_to_secs(duration_str.lower())
                print(duration)

                if duration > 0:
                    response_msg = f'OK. Turning the irrigation on for {self.__convert_secs_to_human_format(duration)}...'
                    success = True
                else:
                    response_msg = 'Invalid duration!'
                    success = False
            except Exception as ex:
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
        rep = {"h": ["hours", "hour", "hrs", "hr"],
               "m": ["minutes", "minute", "mins", "min", "mis", "mi"],
               "s": ["seconds", "second", "secs", "sec"],
               }

        rep = dict((re.escape(v), k) for k, x in rep.items() for v in x)
        pattern = re.compile("|".join(rep.keys()))
        duration_str = pattern.sub(lambda m: rep[re.escape(m.group(0))], duration_str)

        print(duration_str)
        midnight_plus_time = parser.parse(duration_str)
        midnight: datetime = datetime.combine(datetime.today(), datetime.min.time())
        timedelta = midnight_plus_time - midnight
        return timedelta.seconds

    @staticmethod
    def __convert_secs_to_human_format(seconds):
        duration_units = (
            ('day', 60 * 60 * 24),
            ('hour', 60 * 60),
            ('minute', 60),
            ('second', 1)
        )

        if seconds == 0:
            return '0 second'

        parts = []
        for unit, div in duration_units:
            amount, seconds = divmod(int(seconds), div)
            if amount > 0:
                parts.append('{} {}{}'.format(amount, unit, "" if amount == 1 else "s"))
        return ' '.join(parts)
