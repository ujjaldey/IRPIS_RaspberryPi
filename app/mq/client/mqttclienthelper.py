import json
from datetime import datetime

from app.bot.telegrambot import TelegramBot
from app.model.execution import Execution

TYPE_COMMAND = 'COMMAND'
TYPE_ALIVE = 'ALIVE'
TYPE_STATUS = 'STATUS'
STATUS_ON = 'ON'
STATUS_OFF = 'OFF'


class MqttClientHelper:
    def _on_connect(self, mqtt_broker, client, userdata, rc):
        self.logger.info(f'Connected to MQTT broker with result code {str(rc)}')
        self._is_connected = (rc == 0)
        mqtt_broker.subscribe(self.config.get_mqtt_response_topic())

    def _on_message(self, client, userdata, msg):
        msg_str = str(msg.payload.decode('utf-8'))
        self.logger.info(f'Received topic {msg.topic} with message: {msg_str}')

        telegram_bot = TelegramBot(self.logger, self.config)

        resp_sender, resp_success, resp_type, resp_status, resp_duration, resp_execution_id, resp_message = \
            self.__parse_response(msg_str)

        if self.__validate_response(self.config.get_mqtt_response_topic(), self.config.get_mqtt_sender(), msg.topic,
                                    resp_type, resp_sender):
            if resp_type == TYPE_COMMAND:
                success_str = '' if resp_success else 'could not be '
                status_str = resp_status
                message = f'Irrigation {success_str}turned {status_str.lower()}!'

                duration = int(resp_duration)

                if not resp_success:
                    message += '\nError: ' + resp_message
                    success, execution_id = self.execution_dao.update_status(self.conn, resp_execution_id, 'FAILED',
                                                                             resp_message)
                else:
                    if status_str == STATUS_ON:
                        self.display.set_active(True, duration)
                        self.display.display_on_off(True)
                        self.set_execution_id(resp_execution_id)
                        success, execution_id = self.execution_dao.update_status(self.conn, resp_execution_id,
                                                                                 'STARTED', '')
                    elif status_str == STATUS_OFF:
                        self.display.set_active(False)
                        self.display.display_on_off(True)
                        success, execution_id = self.execution_dao.update_status(self.conn, resp_execution_id,
                                                                                 'COMPLETED', '')
                        self.set_execution_id(0)

                telegram_bot.send_response(message)
            elif resp_type == TYPE_ALIVE:
                self.display.set_esp8266_online(True)
            elif resp_type == TYPE_STATUS:
                if not resp_success:
                    message = 'Error while getting the status'
                else:
                    duration_str = f' for {self.util.convert_secs_to_human_format(int(resp_duration))}' if resp_status == STATUS_ON else ''
                    message = f'{resp_message}! Currently the payload is {resp_status.lower()}{duration_str}.'

                telegram_bot.send_response(message)
        else:
            message = 'Invalid response'
            telegram_bot.send_response(message)
            success, execution_id = self.execution_dao.update_status(self.conn, resp_execution_id, 'FAILED', message)

    def esp8266_status(self):
        self.mqtt_client.publish(self.config.get_mqtt_command_topic(),
                                 self.build_mqtt_payload('STATUS'))
        self.display.display_on_off(True)

    def turn_on_payload(self, duration, trigger_type):
        execution = Execution(
            id=0,
            executed_at=datetime.now().replace(microsecond=0),
            duration=duration,
            type=trigger_type.upper(),
            status='INITIATED',
            error='',
            created_at=datetime.now().replace(microsecond=0),
            updated_at=datetime.now().replace(microsecond=0))
        success, execution_id = self.execution_dao.insert(self.conn, execution)

        self.mqtt_client.publish(self.config.get_mqtt_command_topic(),
                                 self.build_mqtt_payload('ON', duration, execution_id))

    def turn_off_payload(self):
        self.mqtt_client.publish(self.config.get_mqtt_command_topic(),
                                 self.build_mqtt_payload('OFF', 0, self.execution_id))

    @staticmethod
    def build_mqtt_payload(action, duration=0, execution_id=0):
        # TODO parameterize
        sender = 'IRPIS-RPI'
        sender_str = f'\"sender\": \"{sender}\",'
        action_str = f'\"action\": \"{action}\",'
        duration_str = f'\"duration\": \"{duration}\",' if action == 'ON' else ''
        execution_id_str = f'\"execution_id\": \"{execution_id}\"'

        return f'{{{sender_str} {action_str} {duration_str} {execution_id_str}'

    @staticmethod
    def __parse_response(response):
        data = json.loads(response)
        resp_sender = data.get('sender') if (data.get('sender') is not None) else ''
        resp_success_str = data.get('success') if (data.get('success') is not None) else ''
        resp_type = data.get('type') if (data.get('type') is not None) else ''
        resp_status = data.get('status') if (data.get('status') is not None) else ''
        resp_duration = data.get('duration') if (data.get('duration') is not None) else ''
        resp_execution_id = data.get('execution_id') if (data.get('execution_id') is not None) else ''
        resp_message = data.get('message') if (data.get('message') is not None) else ''

        resp_success = resp_success_str == 'true'

        return resp_sender, resp_success, resp_type, resp_status, resp_duration, resp_execution_id, resp_message

    @staticmethod
    def __validate_response(mqtt_topic, mqtt_sender, topic, msg_type, sender):
        return sender == mqtt_sender and topic == mqtt_topic and msg_type in [TYPE_COMMAND, TYPE_ALIVE, TYPE_STATUS]
