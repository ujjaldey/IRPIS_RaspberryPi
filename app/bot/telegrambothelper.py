import re
from datetime import datetime

from dateutil import parser
from telegram import Update
from telegram.ext import CallbackContext

from app.dao.execution_dao import ExecutionDao
from app.dao.next_schedule_dao import NextScheduleDao


class TelegramBotHelper:
    def _greet_message(self):
        self.updater.bot.send_message(chat_id=self.config.get_telegram_chat_id(),
                                      text='<b><i>IOT Remote Plant Irrigation System (IRPIS)</i></b> initiating...')

    def _status(self, update: Update, context: CallbackContext):
        self.mqtt_client.esp8266_status()

    def _wakeup(self, update: Update, context: CallbackContext):
        response_msg = 'OK. Turning on the display...'
        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)
        self.display.display_on_off(True)

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

    def _next(self, update: Update, context: CallbackContext):
        self.logger.info('_next is called')

        next_schedule_dao = NextScheduleDao()
        schedule = next_schedule_dao.select(self.conn)

        schedule_time = schedule.next_schedule_at.strftime('%H:%M')

        response_msg = f'Next Execution:' + \
                       f'\n{self.util.convert_date_to_human_format(schedule.next_schedule_at)} at {schedule_time} ' + \
                       f'for {self.util.convert_secs_to_human_format(schedule.duration)}'
        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)

    def _last(self, update: Update, context: CallbackContext):
        self.logger.info('_last is called')

        execution_dao = ExecutionDao()
        execution = execution_dao.select_latest(self.conn)

        execution_date = execution.executed_at
        execution_time = execution.executed_at.strftime('%H:%M')

        response_msg = f'Last Run:' + \
                       f'\n{self.util.convert_date_to_human_format(execution_date)} at {execution_time} ' + \
                       f'for {self.util.convert_secs_to_human_format(execution.duration)} ' + \
                       f'({execution.type.capitalize()})'
        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)

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
