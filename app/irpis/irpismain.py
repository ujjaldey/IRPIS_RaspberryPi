import datetime
from time import sleep

from app.dao.execution_dao import ExecutionDao
from app.dao.next_schedule_dao import NextScheduleDao
from app.dao.schedule_dao import ScheduleDao
from app.irpis.irpismainhelper import IrpisMainHelper
from app.model.next_schedule import NextSchedule


class IrpisMain(IrpisMainHelper):
    def __init__(self, logger, config, db):
        self.logger = logger
        self.config = config
        self.db = db
        self.conn = db.connect().execution_options(autocommit=True)

        self.display = None
        self.mqtt_client = None

    def set_display(self, display):
        self.display = display

    def set_mqtt_client(self, mqtt_client):
        self.mqtt_client = mqtt_client

    def start(self):
        while True:
            self.logger.info("Calling IRPIS main")
            # TODO should be checked at certain interval only
            self.display.set_wifi_online(self._is_internet_connected())

            schedule_dao = ScheduleDao()

            next_schedule_dao = NextScheduleDao()
            schedule = next_schedule_dao.select(self.conn)

            next_schedule, duration = (schedule.next_schedule_at, schedule.duration) if schedule else (None, 0)
            self.display.set_next_schedule(next_schedule,
                                           duration)  # @TODO pass schedule as param, like execution below

            execution_dao = ExecutionDao()
            execution = execution_dao.select_latest(self.conn)

            self.display.set_last_execution(execution)

            if datetime.datetime.now() >= next_schedule:
                for x in schedule_dao.select(self.conn):
                    print(x.id, x.schedule_time, x.duration)

                self.mqtt_client.turn_on_payload(duration, 'SCHEDULED')
                schedule = NextSchedule(
                    next_schedule_at=datetime.datetime.now().replace(microsecond=0) + datetime.timedelta(minutes=5),
                    duration=15, created_at=datetime.datetime.now().replace(microsecond=0),
                    updated_at=datetime.datetime.now().replace(microsecond=0))
                success = next_schedule_dao.upsert(self.conn, schedule)

            sleep(1)
