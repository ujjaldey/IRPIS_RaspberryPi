from dotenv import dotenv_values


class Config:
    def __init__(self):
        self.config = dotenv_values('.env')

    def get_display_change_duration_sec(self):
        return int(self.config['DISPLAY_CHANGE_DURATION_SEC'])

    def get_display_timeout_sec(self):
        return int(self.config['DISPLAY_TIMEOUT_SEC'])

    def get_telegram_bot_name(self):
        return self.config['TELEGRAM_BOT_NAME']

    def get_telegram_api_key(self):
        return self.config['TELEGRAM_API_KEY']

    def get_telegram_chat_id(self):
        return self.config['TELEGRAM_CHAT_ID']

    def get_ping_url(self):
        return self.config['PING_URL']

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

    def get_mqtt_broker(self):
        return self.config['MQTT_BROKER']

    def get_mqtt_client(self):
        return self.config['MQTT_CLIENT']

    def get_database_connection(self):
        return self.config['DATABASE_CONNECTION']

    def get_database_file(self):
        return self.config['DATABASE_FILE']

    def get_history_command_num_rows(self):
        return int(self.config['HISTORY_COMMAND_NUM_ROWS'])

    def get_default_payload_duration_sec(self):
        return int(self.config['DEFAULT_PAYLOAD_DURATION_SEC'])
