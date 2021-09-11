import paho.mqtt.client as mqtt
from app.broker.mqttbrokerhelper import MqttBrokerHelper


class MqttBroker(MqttBrokerHelper):
    def __init__(self, config, logger):
        self._set_logger(logger)
        self._set_config(config)

        self.client = mqtt.Client()

    def set_display(self, display):
        self._set_display(display)

    def connect(self):
        mqtt_server = self.config.get_mqtt_server()
        mqtt_port = self.config.get_mqtt_port()
        mqtt_user = self.config.get_mqtt_user()
        mqtt_password = self.config.get_mqtt_password()

        self.logger.info(f'Connecting to MQTT broker {mqtt_server}')
        self.client.connect(mqtt_server, mqtt_port, 60)
        self.client.username_pw_set(mqtt_user, mqtt_password)

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        self.client.loop_start()

        return self.client
