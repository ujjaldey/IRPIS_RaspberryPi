import datetime
from datetime import datetime
from time import sleep

from app.dao.execution_dao import ExecutionDao
from app.dao.next_schedule_dao import NextScheduleDao
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
        while True:
            self.logger.info("Calling IRPIS main")
            # TODO should be checked at certain interval only
            self.display.set_wifi_online(self._is_internet_connected())

            next_schedule_dao = NextScheduleDao()
            schedule = next_schedule_dao.select(self.conn)

            next_schedule, duration = (schedule.next_schedule_at, schedule.duration) if schedule else (None, 0)
            # @TODO pass schedule as param, like execution below
            self.display.set_next_schedule(next_schedule, duration)

            execution_dao = ExecutionDao()
            execution = execution_dao.select_latest(self.conn)

            self.display.set_last_execution(execution)

            if datetime.now() >= next_schedule:
                self.mqtt_client.turn_on_payload(duration, 'SCHEDULED')

                now = datetime.now().replace(microsecond=0)
                next_schedule, next_duration = self._calculate_next_schedule_and_duration(self.conn, now)

                schedule = NextSchedule(
                    next_schedule_at=next_schedule, duration=next_duration,
                    created_at=datetime.now().replace(microsecond=0),
                    updated_at=datetime.now().replace(microsecond=0))
                success = next_schedule_dao.upsert(self.conn, schedule)

            sleep(1)
