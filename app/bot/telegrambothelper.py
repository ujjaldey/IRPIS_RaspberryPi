from datetime import datetime
from time import sleep, time

from prettytable import PrettyTable
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext

from app.dao.execution_dao import ExecutionDao
from app.dao.next_schedule_dao import NextScheduleDao
from app.dao.schedule_dao import ScheduleDao
from app.enum.irpisenum import IrpisEnum
from app.enum.mqttclientenum import MqttClientEnum
from app.model.next_schedule import NextSchedule


class TelegramBotHelper:
    def _greet_message(self):
        self.logger.info('_greet_message is called')
        app_desc = IrpisEnum.APPLICATION_DESC.value
        app_name = IrpisEnum.APPLICATION_NAME.value

        response_msg = (f'Hi there! <b>{self.common.greet_time()}!</b>\n\n'
                        f'Initiating <b><i>{app_desc} ({app_name})</i></b>...\n\n'
                        'Enter /help for a list of commands...\n')

        self.updater.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)

    def _help(self, update: Update, context: CallbackContext):
        self.logger.info('_help is called')

        response_msg = ('I can help you trigger and control the <b><i>IRPIS</i></b> application via Telegram.\n\n'
                        'You can control me by sending these commands:\n\n'
                        '/help - show the list of commands\n\n'
                        '<b>Control:</b>\n'
                        '/wakeup - wake up the display\n'
                        '/on - turn on the payload for specific time\n'
                        '/off - turn off the payload\n'
                        '/skip - skip the next execution\n\n'
                        '<b>History:</b>\n'
                        '/status - show the current status\n'
                        '/schedule - show the list of schedules\n'
                        '/next - show the next schedule details\n'
                        '/last - show the last execution details\n'
                        '/history - list the history of executions\n\n'
                        '<b>Terminate:</b>\n'
                        '/reboot - reboot the controller unit (Raspberry Pi)\n'
                        '/shutdown - shutdown the controller unit (Raspberry Pi)\n')

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)

        cmd_keyboard = [
            [
                InlineKeyboardButton('/wakeup', callback_data='help_wakeup'),
                InlineKeyboardButton('/on', callback_data='help_on'),
                InlineKeyboardButton('/off', callback_data='help_off'),
                InlineKeyboardButton('/skip', callback_data='help_skip'),
            ],
            [
                InlineKeyboardButton('/status', callback_data='help_status'),
                InlineKeyboardButton('/schedule', callback_data='help_schedule'),
                InlineKeyboardButton('/next', callback_data='help_next'),
                InlineKeyboardButton('/last', callback_data='help_last'),
                InlineKeyboardButton('/history', callback_data='help_history'),
            ],
            [
                InlineKeyboardButton('/reboot', callback_data='help_reboot'),
                InlineKeyboardButton('/shutdown', callback_data='help_shutdown'),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(cmd_keyboard)

        response_msg = 'Select a command for detailed help:'

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg, reply_markup=reply_markup)

    def _detailed_help(self, update: Update, context: CallbackContext):
        query = update.callback_query
        query.answer()

        help_topic = query.data.split('_')[1]

        if help_topic == 'wakeup':
            response_msg = (
                '<b>Command /wakeup:</b>\n\n'
                'Wake up the display of the controller unit. You can change the display timeout duration by changing '
                'the <code>DISPLAY_TIMEOUT_SEC</code> parameter in <code>.env</code> file.\n')
        elif help_topic == 'on':
            response_msg = (
                '<b>Command /on:</b>\n\n'
                'Turn on the irrigation payload (ESP8266) for the specified duration. Pass the duration as an '
                'argument with the command. Throw error if the payload is already in <code>ON</code> state.\n\n'
                'Examples:\n'
                '<code>/on 30sec</code>\n'
                '<code>/on 90 sec</code>\n'
                '<code>/on 1m 10s</code>\n'
                '<code>/on 2 min 20 sec</code>\n'
                '<code>/on 1h2m3s</code>\n\n'
                'Supported time notations:\n'
                'seconds: <code>s</code>, <code>sec</code>, <code>secs</code>, <code>second</code>, '
                '<code>seconds</code>\n'
                'minutes: <code>m</code>, <code>mi</code>, <code>mis</code>, <code>min</code>, <code>mins</code>, '
                '<code>minute</code>, <code>minutes</code>\n'
                'hours: <code>h</code>, <code>hr</code>, <code>hrs</code>, <code>hour</code>, <code>hours</code>\n'
            )
        elif help_topic == 'off':
            response_msg = (
                '<b>Command /off:</b>\n\n'
                'Turn off the irrigation payload unit (ESP8266). Throw error if the payload is already in '
                '<code>OFF</code> state.\n\n')
        elif help_topic == 'skip':
            response_msg = (
                '<b>Command /skip:</b>\n\n'
                'Skip the next scheduled execution.\n\n')
        elif help_topic == 'status':
            response_msg = (
                '<b>Command /status:</b>\n\n'
                'Show the current payload status of the application along with the details of the last execution '
                'and next schedule.\n\n')
        elif help_topic == 'schedule':
            response_msg = (
                '<b>Command /schedule:</b>\n\n'
                'Show the list of schedules along with the durations.')
        elif help_topic == 'next':
            response_msg = (
                '<b>Command /next:</b>\n\n'
                'Show the next scheduled execution time and duration.')
        elif help_topic == 'last':
            response_msg = (
                '<b>Command /last:</b>\n\n'
                'Show the last execution time and duration.')
        elif help_topic == 'history':
            response_msg = (
                '<b>Command /history:</b>\n\n'
                'Show the list of previous execution times and durations. You can change the display timeout '
                'duration by changing the <code>HISTORY_COMMAND_NUM_ROWS</code> parameter in <code>.env</code> file.\n')
        elif help_topic == 'reboot':
            response_msg = (
                '<b>Command /reboot:</b>\n\n'
                'Reboot the controller unit (Raspberry Pi). You need to reboot the payload unit (ESP8266) manually, '
                'if needed.')
        elif help_topic == 'shutdown':
            response_msg = (
                '<b>Command /shutdown:</b>\n\n'
                'Shutdown the controller unit (Raspberry Pi). Once shutdown, you have to turn on the controller unit '
                '(Raspberry Pi) manually.')
        else:
            response_msg = 'Invalid command for help'

        query.edit_message_text(text=response_msg)

    def _status(self, update: Update, context: CallbackContext):
        self.mqtt_client.esp8266_status()

        app_uptime = time() - self.app_start_time
        app_uptime_msg = f'The application is running for {self.common.convert_secs_to_human_format(app_uptime)}.'

        for i in range(1, 10):
            response = self.mqtt_client.get_esp8266_response()
            self.mqtt_client.set_esp8266_response(None)
            if response:
                break
            sleep(0.5)

        if response:
            if response['success']:
                esp8266_response_msg = 'ESP8266 is running and connected.'
                status = response['status']
                duration = response['duration']
                duration_str = f' for {self.common.convert_secs_to_human_format(duration)}' \
                    if status == MqttClientEnum.STATUS_ON.value else ''
                payload_msg = f'Currently the payload is <code>{status}</code>{duration_str}.'
            else:
                esp8266_response_msg = 'Error: ESP8266 is having some issues.'
                payload_msg = ''
        else:
            esp8266_response_msg = 'Error: ESP8266 is either down or not accessible.'

        internet_status = self.common.is_internet_connected(self.config.get_ping_url())
        internet_response_msg = ('' if internet_status else 'Error: ') + 'Internet is ' + \
                                ('connected' if internet_status else 'not connected') + '.'

        execution_dao = ExecutionDao()
        execution = execution_dao.select_latest(self.conn)

        if execution.executed_at:
            last_execution_at = self.common.convert_date_to_human_format(
                execution.executed_at) + ' at ' + execution.executed_at.strftime('%H:%M')
            last_execution_msg = f'Last execution was {last_execution_at} for ' \
                                 f'{self.common.convert_secs_to_human_format(execution.duration, True)} ' \
                                 f'({execution.type.capitalize()}).'
        else:
            last_execution_msg = 'No previous executions.'

        next_schedule_dao = NextScheduleDao()
        schedule = next_schedule_dao.select(self.conn)

        next_schedule, duration = (schedule.next_schedule_at, schedule.duration) if schedule else (None, 0)
        next_schedule_at = self.common.convert_date_to_human_format(next_schedule) + ' at ' + next_schedule.strftime(
            '%H:%M')

        if next_schedule:
            next_schedule_msg = f'Next schedule is {next_schedule_at} for ' \
                                f'{self.common.convert_secs_to_human_format(duration, True)}.'
        else:
            next_schedule_msg = ''

        response_msg = (
            f'{app_uptime_msg}\n\n'
            f'{esp8266_response_msg}\n'
            f'{internet_response_msg}\n\n'
            f'{payload_msg}\n\n'
            f'{last_execution_msg}\n'
            f'{next_schedule_msg}')

        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)
        self.display.display_on_off(True)

    def _wakeup(self, update: Update, context: CallbackContext):
        self.logger.info('_wakeup is called')
        response_msg = 'OK. Turning on the display...'
        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)
        self.display.display_on_off(True)

    def _on(self, update: Update, context: CallbackContext):
        self.logger.info('_on is called')

        duration = 0

        if len(context.args) < 1:
            response_msg = 'Error: No duration entered!\n\nEnter /help for help.'
            success = False
        else:
            try:
                duration_str = ' '.join(context.args)
                duration = self.common.convert_duration_to_secs(duration_str.lower())

                if duration > 0:
                    response_msg = \
                        f'OK. Turning the irrigation payload <code>ON</code> for {self.common.convert_secs_to_human_format(duration)}...'
                    success = True
                else:
                    response_msg = 'Error: Invalid duration!\n\nEnter /help for help.'
                    success = False
            except Exception as ex:
                response_msg = 'Error: Invalid duration!\n\nEnter /help for help.'
                success = False

        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)

        if success:
            self.mqtt_client.turn_on_payload(duration, MqttClientEnum.TRIGGER_MANUAL.value)

    def _off(self, update: Update, context: CallbackContext):
        self.logger.info('_off is called')

        response_msg = 'OK. Turning the irrigation payload <code>OFF</code>...'
        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)

        self.mqtt_client.turn_off_payload()

    def _next(self, update: Update, context: CallbackContext):
        self.logger.info('_next is called')

        next_schedule_dao = NextScheduleDao()
        schedule = next_schedule_dao.select(self.conn)

        schedule_time = schedule.next_schedule_at.strftime('%H:%M')

        response_msg = (
            'Next schedule:\n\n'
            f'<b>{self.common.convert_date_to_human_format(schedule.next_schedule_at)}</b> at <b>{schedule_time}</b> '
            f'for <b>{self.common.convert_secs_to_human_format(schedule.duration)}</b>.')

        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)

    def _last(self, update: Update, context: CallbackContext):
        self.logger.info('_last is called')

        execution_dao = ExecutionDao()
        execution = execution_dao.select_latest(self.conn)

        execution_date = execution.executed_at
        execution_time = execution.executed_at.strftime('%H:%M')

        response_msg = (
            'Last execution:\n\n'
            f'<b>{self.common.convert_date_to_human_format(execution_date)}</b> at <b>{execution_time}</b> '
            f'for <b>{self.common.convert_secs_to_human_format(execution.duration)}</b> '
            f'(<b>{execution.type.capitalize()}</b>).')

        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)

    def _skip(self, update: Update, context: CallbackContext):
        self.logger.info('_skip is called')

        next_schedule_dao = NextScheduleDao()
        curr_schedule = next_schedule_dao.select(self.conn)
        curr_schedule_at = curr_schedule.next_schedule_at

        curr_schedule_time = curr_schedule.next_schedule_at.strftime('%H:%M')

        next_schedule, next_duration = \
            self.common.calculate_next_schedule_and_duration(self.conn, curr_schedule.next_schedule_at,
                                                             self.config.get_default_payload_duration_sec())
        new_schedule_time = next_schedule.strftime('%H:%M')

        schedule = NextSchedule(
            next_schedule_at=next_schedule, duration=next_duration,
            created_at=datetime.now().replace(microsecond=0),
            updated_at=datetime.now().replace(microsecond=0))
        success = next_schedule_dao.upsert(self.conn, schedule)

        response_msg = (
            f'Ok. The next schedule for {self.common.convert_date_to_human_format(curr_schedule_at)} '
            f'at {curr_schedule_time} for {self.common.convert_secs_to_human_format(curr_schedule.duration)} '
            f'will be skipped.\n\n'
            f'New schedule is <b>{self.common.convert_date_to_human_format(next_schedule)}</b> at <b>'
            f'{new_schedule_time}</b> for <b>{self.common.convert_secs_to_human_format(next_duration)}</b>.')
        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)

    def _history(self, update: Update, context: CallbackContext):
        self.logger.info('_history is called')

        table2 = PrettyTable()

        num_of_rows = self.config.get_history_command_num_rows()
        execution_dao = ExecutionDao()
        executions = execution_dao.select(self.conn, num_of_rows)

        if len(executions) > 0:
            table2.field_names = ['Date & Time', 'Duration', 'Type', 'Status']

            for execution in executions:
                execution_time = execution.executed_at.strftime('%H:%M')
                status_and_error = execution.status.capitalize() + (
                    f' ({execution.error})' if execution.status == MqttClientEnum.EXECUTION_FAILED.value else '')

                execution_datetime = (
                    f'{self.common.convert_date_to_human_format(execution.executed_at)} at {execution_time}')

                table2.add_row([
                    execution_datetime,
                    self.common.convert_secs_to_human_format(execution.duration, True),
                    execution.type.capitalize(),
                    status_and_error])

            table2.align = "l"

            num_of_recs = len(executions) if num_of_rows >= len(executions) else num_of_rows
            response_msg = f'Last {str(num_of_recs)} executions:\n\n<pre>{table2}</pre>'
        else:
            response_msg = 'No previous executions'

        # TODO convert to table

        context.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=response_msg)

    def _schedule(self, update: Update, context: CallbackContext):
        self.logger.info('_schedule is called')

        table = PrettyTable()

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
            table.field_names = ['Time', 'Duration']

            for schedule in sorted_schedules:
                schedule_time = schedule[0].strftime('%H:%M')
                schedule_time = schedule_time + ' #' if schedule_time == next_schedule_time else schedule_time

                table.add_row([schedule_time, self.common.convert_secs_to_human_format(schedule[1], True)])

            table.align = "l"

            response_msg = (
                f'List of schedules:\n\n<pre>{table}</pre>\n\n'
                '(<code>#</code>) Next Schedule is '
                f'<b>{self.common.convert_date_to_human_format(next_schedule.next_schedule_at)}</b> at '
                f'<b>{next_schedule_time}</b>')
        else:
            response_msg = 'No schedules'

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

    def _invalid_command(self, update: Update, context: CallbackContext):
        self.logger.info('_invalid_command is called')

        response_msg = f'Opps! I didn\'t get your command {update.message.text}.\n\nTry /help for a list of commands'

        context.bot.send_message(chat_id=update.effective_chat.id, text=response_msg)

    @staticmethod
    def _reboot_confirm(update: Update, context: CallbackContext):
        keyboard = [
            [
                InlineKeyboardButton('Yes', callback_data='reboot_Y'),
                InlineKeyboardButton('No', callback_data='reboot_N'),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text('This command will reboot the Raspberry Pi. Are you sure?', reply_markup=reply_markup)

    @staticmethod
    def _shutdown_confirm(update: Update, context: CallbackContext):
        keyboard = [
            [
                InlineKeyboardButton('Yes', callback_data='shutdown_Y'),
                InlineKeyboardButton('No', callback_data='shutdown_N'),
            ],
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        update.message.reply_text('This command will shutdown the Raspberry Pi. Are you sure?',
                                  reply_markup=reply_markup)

    def _send_response(self, message):
        self.updater.bot.send_message(chat_id=self.config.get_telegram_chat_id(), text=message)

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
                parts.append('{} {}{}'.format(amount, unit, '' if amount == 1 else 's'))
        return ' '.join(parts)
