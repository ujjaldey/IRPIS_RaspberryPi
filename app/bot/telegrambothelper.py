import re
from datetime import datetime
from time import sleep, time

from dateutil import parser
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from app.dao.execution_dao import ExecutionDao
from app.dao.next_schedule_dao import NextScheduleDao
from app.dao.schedule_dao import ScheduleDao
from app.model.next_schedule import NextSchedule


class TelegramBotHelper:
    def _greet_message(self):
        self.updater.bot.send_message(chat_id=self.config.get_telegram_chat_id(),
                                      text='<b><i>IOT Remote Plant Irrigation System (IRPIS)</i></b> initiating...')

    def _status(self, update: Update, context: CallbackContext):
        self.mqtt_client.esp8266_status()

        app_uptime = time() - self.app_start_time
        app_uptime_msg = f'The application is up for {self.common.convert_secs_to_human_format(app_uptime)}'

        for i in range(1, 10):
            response = self.mqtt_client.get_esp8266_response()
            self.mqtt_client.set_esp8266_response(None)
            if response:
                break
            sleep(0.5)

        if response:
            if response['success']:
                esp8266_response_msg = 'ESP8266 is up and running'
                status = response['status']
                duration = response['duration']
                duration_str = f' for {self.common.convert_secs_to_human_format(duration)}' \
                    if status == 'ON' else ''  # TODO reuse enum
                payload_msg = f'Currently the payload is {status.lower()}{duration_str}.'
            else:
                esp8266_response_msg = 'ESP8266 is having some issues'
                payload_msg = ''
        else:
            esp8266_response_msg = 'ESP8266 is either down or not accessible'

        internet_status = self.common.is_internet_connected()
        internet_response_msg = 'Internet is ' + ('connected' if internet_status else 'not connected')

        execution_dao = ExecutionDao()
        execution = execution_dao.select_latest(self.conn)
        last_execution_at = self.common.convert_date_to_human_format(
            execution.executed_at) + ' at ' + execution.executed_at.strftime('%H:%M')
        last_execution_msg = f'Last execution: {last_execution_at} for ' \
                             f'{self.common.convert_secs_to_human_format(execution.duration, True)} ' \
                             f'({execution.type.capitalize()})'

        next_schedule_dao = NextScheduleDao()
        schedule = next_schedule_dao.select(self.conn)

        next_schedule, duration = (schedule.next_schedule_at, schedule.duration) if schedule else (None, 0)
        next_schedule_at = self.common.convert_date_to_human_format(next_schedule) + ' at ' + next_schedule.strftime(
            '%H:%M')
        if next_schedule:
            next_schedule_msg = f'Next schedule: {next_schedule_at} for ' \
                                f'{self.common.convert_secs_to_human_format(duration, True)}'
        else:
            next_schedule_msg = ''

        response_msg = f'Status:\n{app_uptime_msg}\n{esp8266_response_msg}\n{internet_response_msg}' \
                       f'\n{payload_msg}\n{last_execution_msg}\n{next_schedule_msg}'
        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)
        self.display.display_on_off(True)

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
                        f'OK. Turning the irrigation on for {self.common.convert_secs_to_human_format(duration)}...'
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

        response_msg = f'Next Schedule:' + \
                       f'\n{self.common.convert_date_to_human_format(schedule.next_schedule_at)} at {schedule_time} ' + \
                       f'for {self.common.convert_secs_to_human_format(schedule.duration)}'
        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)

    def _last(self, update: Update, context: CallbackContext):
        self.logger.info('_last is called')

        execution_dao = ExecutionDao()
        execution = execution_dao.select_latest(self.conn)

        execution_date = execution.executed_at
        execution_time = execution.executed_at.strftime('%H:%M')

        response_msg = f'Last Run:' + \
                       f'\n{self.common.convert_date_to_human_format(execution_date)} at {execution_time} ' + \
                       f'for {self.common.convert_secs_to_human_format(execution.duration)} ' + \
                       f'({execution.type.capitalize()})'
        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)

    def _skip(self, update: Update, context: CallbackContext):
        self.logger.info('_skip is called')

        next_schedule_dao = NextScheduleDao()
        curr_schedule = next_schedule_dao.select(self.conn)
        curr_schedule_at = curr_schedule.next_schedule_at

        curr_schedule_time = curr_schedule.next_schedule_at.strftime('%H:%M')

        next_schedule, next_duration = self.common.calculate_next_schedule_and_duration(self.conn,
                                                                                        curr_schedule.next_schedule_at)
        new_schedule_time = next_schedule.strftime('%H:%M')

        schedule = NextSchedule(
            next_schedule_at=next_schedule, duration=next_duration,
            created_at=datetime.now().replace(microsecond=0),
            updated_at=datetime.now().replace(microsecond=0))
        success = next_schedule_dao.upsert(self.conn, schedule)

        response_msg = f'Skipped schedule: {self.common.convert_date_to_human_format(curr_schedule_at)} at ' + \
                       f'{curr_schedule_time} for ' + \
                       f'{self.common.convert_secs_to_human_format(curr_schedule.duration)}' + \
                       f'\nNew schedule: {self.common.convert_date_to_human_format(next_schedule)} at ' + \
                       f'{new_schedule_time} for {self.common.convert_secs_to_human_format(next_duration)}'
        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)

    def _history(self, update: Update, context: CallbackContext):
        self.logger.info('_history is called')

        num_of_rows = self.config.get_history_command_num_rows()
        execution_dao = ExecutionDao()
        executions = execution_dao.select(self.conn, num_of_rows)

        if len(executions) > 0:
            log_str = ""
            for execution in executions:
                execution_time = execution.executed_at.strftime('%H:%M')
                status_and_error = execution.status.capitalize() + \
                                   (f' ({execution.error})' if execution.status == 'FAILED' else '')
                log_str += f'\n{self.common.convert_date_to_human_format(execution.executed_at)} at ' + \
                           f'{execution_time} | ' + \
                           f'{self.common.convert_secs_to_human_format(execution.duration, True)} | ' + \
                           f'{execution.type.capitalize()} | {status_and_error}'

            num_of_recs = len(executions) if num_of_rows >= len(executions) else num_of_rows
            response_msg = f'Last {str(num_of_recs)} executions: ' + log_str
        else:
            response_msg = 'No previous executions'

        # TODO convert to table

        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)

    def _schedule(self, update: Update, context: CallbackContext):
        self.logger.info('_schedule is called')

        schedule_dao = ScheduleDao()
        schedule_objs = schedule_dao.select(self.conn)
        today = datetime.now().replace(microsecond=0)
        today_str = today.strftime('%d-%m-%Y')

        schedules = [(datetime.strptime(f'{today_str} {x.schedule_time}', '%d-%m-%Y %H:%M'), x.duration) for x in
                     schedule_objs]

        sorted_schedules = sorted(schedules, key=lambda tup: tup[0])

        next_schedule_dao = NextScheduleDao()
        next_schedule = next_schedule_dao.select(self.conn)
        next_schedule_time = next_schedule.next_schedule_at.strftime('%H:%M')

        if len(sorted_schedules) > 0:
            schedule_str = ""
            for schedule in sorted_schedules:
                schedule_time = schedule[0].strftime('%H:%M')
                schedule_str += f'\n{schedule_time} | ' + \
                                f'{self.common.convert_secs_to_human_format(schedule[1], True)}' + \
                                (' *' if schedule_time == next_schedule_time else '')

            response_msg = f'Schedules: {schedule_str}\n\n' + \
                           '* Next Schedule: ' + \
                           f'{self.common.convert_date_to_human_format(next_schedule.next_schedule_at)} at ' + \
                           f'{next_schedule_time}'
        else:
            response_msg = 'No schedules'

            # TODO convert to table

        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)

    def _reboot(self, update: Update, context: CallbackContext):
        self.logger.info('_reboot is called')

        query = update.callback_query
        query.answer()

        if query.data == 'reboot_Y':
            response_msg = 'Ok. Rebooting in 5 seconds...'
            query.edit_message_text(text=response_msg)
            sleep(5)
            self.common.reboot()
        else:
            response_msg = 'Ok. Command cancelled!'
            query.edit_message_text(text=response_msg)

    def _shutdown(self, update: Update, context: CallbackContext):
        self.logger.info('_shutdown is called')

        query = update.callback_query
        query.answer()

        if query.data == 'shutdown_Y':
            response_msg = 'Ok. Shutting down in 5 seconds...'
            query.edit_message_text(text=response_msg)
            sleep(5)
            self.common.shutdown()
        else:
            response_msg = 'Ok. Command cancelled!'
            query.edit_message_text(text=response_msg)

    @staticmethod
    def _reboot_confirm(update: Update, context: CallbackContext):
        keyboard = [
            [
                InlineKeyboardButton("Yes", callback_data='reboot_Y'),
                InlineKeyboardButton("No", callback_data='reboot_N'),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text('This command will reboot the Raspberry Pi. Are you sure?', reply_markup=reply_markup)

    @staticmethod
    def _shutdown_confirm(update: Update, context: CallbackContext):
        keyboard = [
            [
                InlineKeyboardButton("Yes", callback_data='shutdown_Y'),
                InlineKeyboardButton("No", callback_data='shutdown_N'),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text('This command will shutdown the Raspberry Pi. Are you sure?',
                                  reply_markup=reply_markup)

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
