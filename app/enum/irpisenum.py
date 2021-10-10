from enum import Enum


class IrpisEnum(Enum):
    APPLICATION_NAME = 'IRPIS'
    APPLICATION_DESC_1 = 'IOT Remote'
    APPLICATION_DESC_2 = 'Plant Irrigation System'
    APPLICATION_DESC = f'{APPLICATION_DESC_1} {APPLICATION_DESC_2}'

    CHECK_INTERNET_INTERVAL_SEC = 30
