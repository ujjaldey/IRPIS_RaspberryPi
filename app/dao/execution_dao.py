from datetime import datetime

from sqlalchemy import Column, MetaData, String, Table, Integer, select, func

from app.model.execution import Execution


class ExecutionDao:
    def __init__(self):
        self.table = Table(
            "executions", MetaData(),
            Column("id", Integer, autoincrement=True, nullable=False, primary_key=True, unique=True),
            Column("executed_at", String, nullable=False),
            Column("duration", Integer, nullable=False, default=0),
            Column("type", String, nullable=False),
            Column("status", String),
            Column("error", String),
            Column("created_at", String, nullable=True, default=datetime.now),
            Column("updated_at", String, nullable=True, default=datetime.now)
        )

    def select_latest(self, conn):
        try:
            stmt = select(
                [self.table.c.id, self.table.c.executed_at, self.table.c.duration, self.table.c.type,
                 self.table.c.status, self.table.c.error, self.table.c.created_at, self.table.c.updated_at]) \
                .where(self.table.c.status == 'COMPLETED') \
                .order_by(self.table.c.executed_at.desc())

            out_cur = conn.execute(stmt)
            rec = out_cur.fetchone()

            last_execution = None if not rec['id'] else Execution(
                id=int(rec['id']),
                executed_at=datetime.strptime(rec['executed_at'], '%Y-%m-%d %H:%M:%S'),
                duration=int(rec['duration']),
                type=rec['type'],
                status=rec['status'],
                error=rec['error'],
                created_at=datetime.strptime(rec['created_at'], '%Y-%m-%d %H:%M:%S'),
                updated_at=datetime.strptime(rec['updated_at'], '%Y-%m-%d %H:%M:%S'))

            return last_execution
        except Exception as ex:
            print(ex)
            # self.logger.fatal("Exception in __start_mqtt_telegrambot: " + str(ex), exc_info=True)

    def insert(self, conn, execution):
        stmt = self.table \
            .insert() \
            .values(executed_at=execution.executed_at,
                    duration=execution.duration, type=execution.type, status=execution.status, error=execution.error,
                    created_at=execution.created_at, updated_at=execution.updated_at)

        ret = conn.execute(stmt)
        return True, ret.lastrowid

    def update_status(self, conn, id, status, error):
        stmt = self.table \
            .update() \
            .values(status=status, error=error, updated_at=datetime.now().replace(microsecond=0)) \
            .where(self.table.c.id == id)

        ret = conn.execute(stmt)
        return True, ret.lastrowid