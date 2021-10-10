from enum import Enum


class MqttClientEnum(Enum):
    TYPE_COMMAND = 'COMMAND'
    TYPE_ALIVE = 'ALIVE'
    TYPE_STATUS = 'STATUS'
    STATUS_ON = 'ON'
    STATUS_OFF = 'OFF'
