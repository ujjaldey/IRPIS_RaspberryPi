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
        if msg.topic == "irpis/esp8266/response" and "COMMAND" in str(msg.payload):
            # bot = telegram.Bot(token="1520849970:AAHNMm-gXWHCLZpQ5HN17_ZfdSTZrK6SpAw")
            # bot.send_message(chat_id=1542846687, text="response: " + str(msg.payload))
            pass
