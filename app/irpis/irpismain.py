import datetime
from datetime import datetime
from time import sleep, time

from app.dao.execution_dao import ExecutionDao
from app.dao.next_schedule_dao import NextScheduleDao
from app.enum.irpisenum import IrpisEnum
from app.enum.mqttclientenum import MqttClientEnum
from app.irpis.irpismainhelper import IrpisMainHelper
from app.model.next_schedule import NextSchedule
from app.util.common import Common


class IrpisMain(IrpisMainHelper):
    def __init__(self, logger, config, db):
        self.logger = logger
        self.config = config
        self.db = db
        self.conn = db.connect().execution_options(autocommit=True)

        self.display = None
        self.mqtt_client = None

        self.common = Common()

    def set_display(self, display):
        self.display = display

    def set_mqtt_client(self, mqtt_client):
        self.mqtt_client = mqtt_client

    def start(self):
        self.logger.info(f'Starting {IrpisEnum.APPLICATION_NAME.value} main')
        check_internet_counter_sec = 0

        while True:
            if int(time()) >= check_internet_counter_sec + IrpisEnum.IRPIS_HEARTBEAT_SEC.value:
                self.display.set_wifi_online(self._is_internet_connected())
                check_internet_counter_sec = int(time())

                next_schedule_dao = NextScheduleDao()
                schedule = next_schedule_dao.select(self.conn)

                self.display.set_next_schedule(schedule)
                next_schedule, duration = (schedule.next_schedule_at, schedule.duration) if schedule else (None, 0)

                execution_dao = ExecutionDao()
                execution = execution_dao.select_latest(self.conn)

                self.display.set_last_execution(execution)

                if next_schedule:
                    if datetime.now().replace(microsecond=0) >= next_schedule:
                        self.mqtt_client.turn_on_payload(duration, MqttClientEnum.TRIGGER_SCHEDULED.value)

                        self.__upsert_next_schedule(next_schedule_dao)
                else:
                    self.__upsert_next_schedule(next_schedule_dao)

            sleep(1)

    def __upsert_next_schedule(self, next_schedule_dao):
        now = datetime.now().replace(microsecond=0)
        next_schedule, next_duration = self._calculate_next_schedule_and_duration(self.conn, now)

        schedule = NextSchedule(
            next_schedule_at=next_schedule, duration=next_duration,
            created_at=datetime.now().replace(microsecond=0),
            updated_at=datetime.now().replace(microsecond=0))

        return next_schedule_dao.upsert(self.conn, schedule)
