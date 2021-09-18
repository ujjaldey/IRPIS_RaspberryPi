from datetime import datetime

from sqlalchemy import Column, MetaData, String, Table, Integer, select, and_, func

from app.model.schedule import Schedule


class ScheduleDao:
    def __init__(self):
        self.table = Table(
            "schedules", MetaData(),
            Column("next_schedule", String, nullable=False),
            Column("duration", Integer, nullable=False),
            Column("created_at", String, nullable=True, default=datetime.now),
            Column("updated_at", String, nullable=True, default=datetime.now)
        )

    # def dao_table(self):
    #     return self.table

    def select(self, conn):
        try:
            schedules = []
            stmt = select(
                [self.table.c.next_schedule, self.table.c.duration, self.table.c.created_at,
                 self.table.c.updated_at])

            out_cur = conn.execute(stmt)
            rec = out_cur.fetchone()

            schedule = None if not rec['next_schedule'] else Schedule(
                next_schedule=datetime.strptime(rec['next_schedule'], '%Y-%m-%d %H:%M:%S'),
                duration=int(rec['duration']),
                created_at=datetime.strptime(rec['created_at'], '%Y-%m-%d %H:%M:%S'),
                updated_at=datetime.strptime(rec['updated_at'], '%Y-%m-%d %H:%M:%S'))

            return schedule
        except Exception as ex:
            print(ex)
            # self.logger.fatal("Exception in __start_mqtt_telegrambot: " + str(ex), exc_info=True)

    def upsert(self, conn, schedule):
        try:
            stmt = select(func.count(self.table.c.next_schedule).label('rec_count'))

            out_cur = conn.execute(stmt)
            rec = out_cur.fetchone()

            next_schedule_exists = (rec['rec_count'] > 0)

            if next_schedule_exists:
                stmt = self.table.update().values(next_schedule=schedule.next_schedule, duration=schedule.duration,
                                                  updated_at=schedule.updated_at)
            else:
                stmt = self.table.insert().values(next_schedule=schedule.next_schedule, duration=schedule.duration,
                                                  created_at=schedule.created_at, updated_at=schedule.updated_at)

            ret = conn.execute(stmt)
            return True
        except Exception as ex:
            print(ex)
            # self.logger.fatal("Exception in __start_mqtt_telegrambot: " + str(ex), exc_info=True)
            return False