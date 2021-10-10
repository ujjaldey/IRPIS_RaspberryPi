from datetime import datetime

from sqlalchemy import Column, MetaData, String, Table, Integer, select, func

from app.model.next_schedule import NextSchedule


class NextScheduleDao:
    def __init__(self):
        self.table = Table(
            'next_schedules', MetaData(),
            Column('next_schedule_at', String, nullable=False),
            Column('duration', Integer, nullable=False, default=0),
            Column('created_at', String, nullable=True, default=datetime.now),
            Column('updated_at', String, nullable=True, default=datetime.now)
        )

    def select(self, conn):
        try:
            stmt = select(
                [self.table.c.next_schedule_at, self.table.c.duration, self.table.c.created_at,
                 self.table.c.updated_at])

            out_cur = conn.execute(stmt)
            rec = out_cur.fetchone()

            schedule = self.__parse_cols(rec)

            return schedule
        except Exception as ex:
            print(ex)
            # self.logger.fatal('Exception in __start_mqtt_telegrambot: ' + str(ex), exc_info=True)

    def upsert(self, conn, schedule):
        try:
            stmt = select(func.count(self.table.c.next_schedule_at).label('rec_count'))

            out_cur = conn.execute(stmt)
            rec = out_cur.fetchone()

            next_schedule_exists = (rec['rec_count'] > 0)

            if next_schedule_exists:
                stmt = self.table.update().values(next_schedule_at=schedule.next_schedule_at,
                                                  duration=schedule.duration,
                                                  updated_at=schedule.updated_at)
            else:
                stmt = self.table.insert().values(next_schedule_at=schedule.next_schedule_at,
                                                  duration=schedule.duration,
                                                  created_at=schedule.created_at, updated_at=schedule.updated_at)

            ret = conn.execute(stmt)
            return True
        except Exception as ex:
            print(ex)
            # self.logger.fatal('Exception in __start_mqtt_telegrambot: ' + str(ex), exc_info=True)
            return False

    @staticmethod
    def __parse_cols(rec=None):
        if rec:
            return NextSchedule(
                next_schedule_at=datetime.strptime(rec['next_schedule_at'], '%Y-%m-%d %H:%M:%S'),
                duration=int(rec['duration']),
                created_at=datetime.strptime(rec['created_at'], '%Y-%m-%d %H:%M:%S'),
                updated_at=datetime.strptime(rec['updated_at'], '%Y-%m-%d %H:%M:%S'))
        else:
            return NextSchedule(
                next_schedule_at=None,
                duration=0,
                created_at=None,
                updated_at=None)
