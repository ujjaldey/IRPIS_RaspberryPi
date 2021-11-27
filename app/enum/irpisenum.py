from enum import Enum


class IrpisEnum(Enum):
    APPLICATION_NAME = 'IRPIS'
    APPLICATION_DESC_1 = 'IOT Remote'
    APPLICATION_DESC_2 = 'Plant Irrigation System'
    APPLICATION_DESC = f'{APPLICATION_DESC_1} {APPLICATION_DESC_2}'

    IRPIS_HEARTBEAT_SEC = 5
