from datetime import datetime


class Execution:
    def __init__(self, id, executed_at, duration, type, status, error, created_at=datetime.now().replace(microsecond=0),
                 updated_at=datetime.now().replace(microsecond=0)):
        self.id = id
        self.executed_at = executed_at
        self.duration = duration
        self.type = type
        self.status = status
        self.error = error
        self.created_at = created_at
        self.updated_at = updated_at
