from app.bot.telegrambot import TelegramBot
import json


class MqttBrokerHelper:
    def _set_logger(self, logger):
        self.logger = logger

    def _set_config(self, config):
        self.config = config

    def _on_connect(self, mqtt_broker, client, userdata, rc):
        self.logger.info(f"Connected to MQTT broker with result code {str(rc)}")
        mqtt_broker.subscribe(self.config.get_mqtt_response_topic())

    def _on_message(self, client, userdata, msg):
        print("Topic: ", msg.topic + "\nMessage: " + str(msg.payload))
        msg_sender, msg_success, msg_type, msg_status, resp_message = \
            self.__parse_response(str(msg.payload.decode("utf-8")))

        if msg.topic == "irpis/esp8266/response" and "COMMAND" in str(msg.payload):
            telegram_bot = TelegramBot(self.config, self.logger)
            telegram_bot.send_response(msg_success, msg_status, resp_message)

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
