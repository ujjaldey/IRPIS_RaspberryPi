from datetime import datetime

from sqlalchemy import Column, MetaData, String, Table, Integer, select, func

from app.model.schedule import Schedule


class ScheduleDao:
    def __init__(self):
        self.table = Table(
            "schedules", MetaData(),
            Column("id", Integer, autoincrement=True, nullable=False, primary_key=True, unique=True),
            Column("schedule_time", String, nullable=False),
            Column("duration", Integer, nullable=False, default=0),
            Column("active", String, nullable=False),
            Column("created_at", String, nullable=True, default=datetime.now),
            Column("updated_at", String, nullable=True, default=datetime.now)
        )

    def select(self, conn):
        try:
            stmt = select(
                [self.table.c.id, self.table.c.schedule_time, self.table.c.duration, self.table.c.active,
                 self.table.c.created_at, self.table.c.updated_at]) \
                .where(self.table.c.active == 'Y') \
                .order_by(self.table.c.id.asc())

            out_cur = conn.execute(stmt)

            schedules = []

            for rec in out_cur:
                schedule = None if not rec['id'] else Schedule(
                    id=int(rec['id']),
                    schedule_time=rec['schedule_time'],
                    duration=int(rec['duration']),
                    active=rec['active'],
                    created_at=datetime.strptime(rec['created_at'], '%Y-%m-%d %H:%M:%S'),
                    updated_at=datetime.strptime(rec['updated_at'], '%Y-%m-%d %H:%M:%S'))

                schedules.append(schedule)

            return schedules
        except Exception as ex:
            print(ex)
            # self.logger.fatal("Exception in __start_mqtt_telegrambot: " + str(ex), exc_info=True)
