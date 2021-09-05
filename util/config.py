from dotenv import dotenv_values


class Config:
    def __init__(self):
        self.config = dotenv_values('.env')

    def get_telegram_bot_name(self):
        return self.config['TELEGRAM_BOT_NAME']

    def get_telegram_api_key(self):
        return self.config['TELEGRAM_API_KEY']

    def get_mqtt_server(self):
        return self.config['MQTT_SERVER']

    def get_mqtt_port(self):
        return int(self.config['MQTT_PORT'])

    def get_mqtt_user(self):
        return self.config['MQTT_USER']

    def get_mqtt_password(self):
        return self.config['MQTT_PASSWORD']

    def get_mqtt_command_topic(self):
        return self.config['MQTT_COMMAND_TOPIC']

    def get_mqtt_response_topic(self):
        return self.config['MQTT_RESPONSE_TOPIC']
