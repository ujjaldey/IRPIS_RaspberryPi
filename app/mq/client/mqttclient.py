from app.dao.execution_dao import ExecutionDao
from app.mq.broker.mqttbroker import MqttBroker
from app.mq.client.mqttclienthelper import MqttClientHelper
from app.util.common import Common


class MqttClient(MqttClientHelper):
    def __init__(self, logger, config, db):
        self.logger = logger
        self.config = config
        self.db = db
        self.conn = db.connect().execution_options(autocommit=True)
        self.execution_dao = ExecutionDao()

        self.mqtt_broker = MqttBroker(config, logger)
        self.mqtt_client = None
        self._is_connected = False
        self.display = None
        self.execution_id = 0

        self.common = Common()

        self.__esp8266_response = None

    def set_esp8266_response(self, esp8266_response):
        self.__esp8266_response = esp8266_response

    def get_esp8266_response(self):
        return self.__esp8266_response

    def connect(self):
        self.mqtt_client = self.mqtt_broker.connect()

        self.mqtt_client.on_connect = self._on_connect
        self.mqtt_client.on_message = self._on_message

        self.mqtt_client.loop_start()

    def set_display(self, display):
        self.display = display

    def set_execution_id(self, execution_id):
        self.execution_id = execution_id

    def is_connected(self):
        return self._is_connected
