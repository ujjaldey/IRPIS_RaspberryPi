import re
from datetime import datetime

from dateutil import parser
from telegram import Update
from telegram.ext import CallbackContext


class TelegramBotHelper:
    def _greet_message(self):
        self.updater.bot.send_message(chat_id=self.config.get_telegram_chat_id(),
                                      text='<b><i>IOT Remote Plant Irrigation System (IRPIS)</i></b> initiating...')

    def _status(self, update: Update, context: CallbackContext):
        self.mqtt_client.esp8266_status()

    def _on(self, update: Update, context: CallbackContext):
        self.logger.info('_on is called')

        duration = 0

        if len(context.args) < 1:
            response_msg = 'Enter the duration!'
            success = False
        else:
            try:
                duration_str = " ".join(context.args)
                duration = self.__convert_duration_to_secs(duration_str.lower())

                if duration > 0:
                    response_msg = \
                        f'OK. Turning the irrigation on for {self.util.convert_secs_to_human_format(duration)}...'
                    success = True
                else:
                    response_msg = 'Invalid duration!'
                    success = False
            except Exception as ex:
                response_msg = 'Invalid duration!'
                success = False

        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)

        if success:
            self.mqtt_client.turn_on_payload(duration, 'MANUAL')

    def _off(self, update: Update, context: CallbackContext):
        self.logger.info('_off is called')

        response_msg = 'OK. Turning the irrigation off...'
        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)

        self.mqtt_client.turn_off_payload()

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
