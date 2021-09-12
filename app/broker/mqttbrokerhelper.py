from app.bot.telegrambot import TelegramBot
import json

TYPE_COMMAND = 'COMMAND'
TYPE_ALIVE = 'ALIVE'
STATUS_ON = 'on'
STATUS_OFF = 'off'


class MqttBrokerHelper:
    def _set_logger(self, logger):
        self.logger = logger

    def _set_config(self, config):
        self.config = config

    def _set_display(self, display):
        self.display = display

    def _on_connect(self, mqtt_broker, client, userdata, rc):
        self.logger.info(f'Connected to MQTT broker with result code {str(rc)}')
        mqtt_broker.subscribe(self.config.get_mqtt_response_topic())

    def _on_message(self, client, userdata, msg):
        msg_str = str(msg.payload.decode('utf-8'))
        self.logger.info(f'Received topic {msg.topic} with message: {msg_str}')

        telegram_bot = TelegramBot(self.config, self.logger)

        resp_sender, resp_success, resp_type, resp_status, resp_message = \
            self.__parse_response(msg_str)

        if self.__validate_response(self.config.get_mqtt_response_topic(), self.config.get_mqtt_sender(), msg.topic,
                                    resp_type, resp_sender):
            if resp_type == TYPE_COMMAND:
                success_str = '' if resp_success else 'could not be '
                status_str = resp_status.lower()
                message = f'Irrigation {success_str}turned {status_str}!'

                # TODO. Modify the ESP code to return the duration as part of response. and parse it here
                duration = 10

                if not resp_success:
                    message += '\nError: ' + resp_message
                else:
                    print("-----------------", status_str)
                    if status_str == STATUS_ON:
                        self.display.set_active(True, duration)
                        self.display.enable_backlight(True)
                    elif status_str == STATUS_OFF:
                        self.display.set_active(False)
                        self.display.enable_backlight(True)

                telegram_bot.send_response(message)
        else:
            message = 'Invalid response'
            telegram_bot.send_response(message)

    @staticmethod
    def __parse_response(response):
        data = json.loads(response)
        resp_sender = data.get('sender') if (data.get('sender') is not None) else ''
        resp_success_str = data.get('success') if (data.get('success') is not None) else ''
        resp_type = data.get('type') if (data.get('type') is not None) else ''
        resp_status = data.get('status') if (data.get('status') is not None) else ''
        resp_message = data.get('message') if (data.get('message') is not None) else ''

        resp_success = resp_success_str == 'true'

        return resp_sender, resp_success, resp_type, resp_status, resp_message

    @staticmethod
    def __validate_response(mqtt_topic, mqtt_sender, topic, type, sender):
        return sender == mqtt_sender and topic == mqtt_topic and type in [TYPE_COMMAND, TYPE_ALIVE]
