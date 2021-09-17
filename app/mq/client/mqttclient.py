import json

from app.mq.broker.mqttbroker import MqttBroker
from app.mq.client.mqttclienthelper import MqttClientHelper


class MqttClient(MqttClientHelper):
    def __init__(self, config, logger):
        self.logger = logger
        self.config = config

        self.mqtt_broker = MqttBroker(config, logger)
        self._is_connected = False
        self.display = None

    def connect(self):
        mqtt_client = self.mqtt_broker.connect()

        mqtt_client.on_connect = self._on_connect
        mqtt_client.on_message = self._on_message

        mqtt_client.loop_start()

        return mqtt_client

    def set_display(self, display):
        self.display = display

    def is_connected(self):
        return self._is_connected
