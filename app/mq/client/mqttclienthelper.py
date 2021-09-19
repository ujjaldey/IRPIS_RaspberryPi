import json
from datetime import datetime

from app.bot.telegrambot import TelegramBot
from app.dao.execution_dao import ExecutionDao
from app.model.execution import Execution

TYPE_COMMAND = 'COMMAND'
TYPE_ALIVE = 'ALIVE'
STATUS_ON = 'on'
STATUS_OFF = 'off'


class MqttClientHelper:
    def _on_connect(self, mqtt_broker, client, userdata, rc):
        self.logger.info(f'Connected to MQTT broker with result code {str(rc)}')
        self._is_connected = (rc == 0)
        mqtt_broker.subscribe(self.config.get_mqtt_response_topic())

    def _on_message(self, client, userdata, msg):
        msg_str = str(msg.payload.decode('utf-8'))
        self.logger.info(f'Received topic {msg.topic} with message: {msg_str}')

        telegram_bot = TelegramBot(self.logger, self.config)

        resp_sender, resp_success, resp_type, resp_status, resp_duration, resp_message = \
            self.__parse_response(msg_str)

        if self.__validate_response(self.config.get_mqtt_response_topic(), self.config.get_mqtt_sender(), msg.topic,
                                    resp_type, resp_sender):
            if resp_type == TYPE_COMMAND:
                success_str = '' if resp_success else 'could not be '
                status_str = resp_status.lower()
                message = f'Irrigation {success_str}turned {status_str}!'

                duration = int(resp_duration)

                if not resp_success:
                    message += '\nError: ' + resp_message
                    # TODO get the exec id from response and update the error message in db
                else:
                    if status_str == STATUS_ON:
                        self.display.set_active(True, duration)
                        self.display.enable_backlight(True)
                        # TODO get the exec id from response, and assign to self.set_execution_id()
                    elif status_str == STATUS_OFF:
                        self.display.set_active(False)
                        self.display.enable_backlight(True)
                        # TODO get the exec id from response and update the status in db

                telegram_bot.send_response(message)
            elif resp_type == TYPE_ALIVE:
                self.display.set_esp8266_online(True)
        else:
            message = 'Invalid response'
            telegram_bot.send_response(message)

    def turn_on_payload(self, duration, trigger_type):
        execution_dao = ExecutionDao()

        execution = Execution(
            id=0,
            executed_at=datetime.now().replace(microsecond=0),
            duration=duration,
            type=trigger_type.upper(),
            status='STARTERD',
            created_at=datetime.now().replace(microsecond=0),
            updated_at=datetime.now().replace(microsecond=0))
        success, execution_id = execution_dao.insert(self.conn, execution)
        self.set_execution_id(execution_id)
        print(success, execution_id)

        self.mqtt_client.publish(self.config.get_mqtt_command_topic(),
                                 f'{{\"sender\": \"IRPIS-RPI\", \"action\": \"ON\", \"duration\": {duration}}}')

    def turn_off_payload(self):
        print("off", self.execution_id)
        self.mqtt_client.publish(self.config.get_mqtt_command_topic(),
                                 '{\"sender\": \"IRPIS-RPI\", \"action\": \"OFF\"}')

    @staticmethod
    def __parse_response(response):
        data = json.loads(response)
        resp_sender = data.get('sender') if (data.get('sender') is not None) else ''
        resp_success_str = data.get('success') if (data.get('success') is not None) else ''
        resp_type = data.get('type') if (data.get('type') is not None) else ''
        resp_status = data.get('status') if (data.get('status') is not None) else ''
        resp_duration = data.get('duration') if (data.get('duration') is not None) else ''
        resp_message = data.get('message') if (data.get('message') is not None) else ''

        resp_success = resp_success_str == 'true'

        return resp_sender, resp_success, resp_type, resp_status, resp_duration, resp_message

    @staticmethod
    def __validate_response(mqtt_topic, mqtt_sender, topic, msg_type, sender):
        return sender == mqtt_sender and topic == mqtt_topic and msg_type in [TYPE_COMMAND, TYPE_ALIVE]
