import json
from datetime import datetime

from app.bot.telegrambot import TelegramBot
from app.enum.mqttclientenum import MqttClientEnum
from app.model.execution import Execution


class MqttClientHelper:
    def _on_connect(self, mqtt_broker, client, userdata, rc):
        self.logger.info(f'Connected to MQTT broker with result code {str(rc)}')
        self._is_connected = (rc == 0)
        mqtt_broker.subscribe(self.config.get_mqtt_response_topic())

    def _on_message(self, client, userdata, msg):
        msg_str = str(msg.payload.decode('utf-8'))
        self.logger.info(f'Received topic {msg.topic} with message: {msg_str}')

        telegram_bot = TelegramBot(self.logger, self.config, self.db, 0)

        resp_sender, resp_success, resp_type, resp_status, resp_duration, resp_execution_id, resp_message = \
            self.__parse_response(msg_str)

        if self.__validate_response(self.config.get_mqtt_response_topic(), self.config.get_mqtt_client(), msg.topic,
                                    resp_type, resp_sender):
            if resp_type == MqttClientEnum.TYPE_COMMAND.value:
                success_str = '' if resp_success else 'could not be '
                status_str = resp_status

                if status_str == MqttClientEnum.STATUS_ON.value:
                    status_str_with_duration = f'{status_str.lower()} for ' \
                                               f'{self.common.convert_secs_to_human_format(int(resp_duration))}'
                else:
                    status_str_with_duration = status_str.lower()

                message = f'Irrigation {success_str}turned {status_str_with_duration}!'

                duration = int(resp_duration)

                if not resp_success:
                    message += '\nError: ' + resp_message
                    success, execution_id = self.execution_dao.update_status(self.conn, resp_execution_id, 'FAILED',
                                                                             resp_message)
                else:
                    if status_str == MqttClientEnum.STATUS_ON.value:
                        self.display.set_active(True, duration)
                        self.display.display_on_off(True)
                        self.set_execution_id(resp_execution_id)
                        success, execution_id = self.execution_dao.update_status(self.conn, resp_execution_id,
                                                                                 'STARTED', '')
                    elif status_str == MqttClientEnum.STATUS_OFF.value:
                        self.display.set_active(False)
                        self.display.display_on_off(True)
                        success, execution_id = self.execution_dao.update_status(self.conn, resp_execution_id,
                                                                                 'COMPLETED', '')
                        self.set_execution_id(0)

                telegram_bot.send_response(message)
            elif resp_type == MqttClientEnum.TYPE_ALIVE.value:
                self.display.set_esp8266_online(True)
            elif resp_type == MqttClientEnum.TYPE_STATUS.value:
                response = {'success': bool(resp_success), 'status': resp_status, 'duration': int(resp_duration)}
                self.set_esp8266_response(response)
        else:
            message = 'Invalid response'
            telegram_bot.send_response(message)
            success, execution_id = self.execution_dao.update_status(self.conn, resp_execution_id, 'FAILED', message)

    def esp8266_status(self):
        self.mqtt_client.publish(self.config.get_mqtt_command_topic(),
                                 self.build_mqtt_payload(MqttClientEnum.TYPE_STATUS.value))
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
                                 self.build_mqtt_payload(MqttClientEnum.STATUS_ON.value, duration, execution_id))

    def turn_off_payload(self):
        self.mqtt_client.publish(self.config.get_mqtt_command_topic(),
                                 self.build_mqtt_payload(MqttClientEnum.STATUS_OFF.value, 0, self.execution_id))

    def build_mqtt_payload(self, action, duration=0, execution_id=0):
        sender = self.config.get_mqtt_broker()
        sender_str = f'\"sender\": \"{sender}\",'
        action_str = f'\"action\": \"{action}\",'
        duration_str = f'\"duration\": \"{duration}\",' if action == MqttClientEnum.STATUS_ON.value else ''
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
        return sender == mqtt_sender and topic == mqtt_topic and msg_type in [MqttClientEnum.TYPE_COMMAND.value,
                                                                              MqttClientEnum.TYPE_ALIVE.value,
                                                                              MqttClientEnum.TYPE_STATUS.value]
