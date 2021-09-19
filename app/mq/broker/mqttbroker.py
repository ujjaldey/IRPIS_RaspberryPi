import paho.mqtt.client as mqtt


class MqttBroker:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger

        self.client = mqtt.Client()

    def connect(self):
        mqtt_server = self.config.get_mqtt_server()
        mqtt_port = self.config.get_mqtt_port()
        mqtt_user = self.config.get_mqtt_user()
        mqtt_password = self.config.get_mqtt_password()

        self.logger.info(f'Connecting to MQTT broker {mqtt_server}')
        self.client.connect(mqtt_server, mqtt_port, 60)
        self.client.username_pw_set(mqtt_user, mqtt_password)

        return self.client
