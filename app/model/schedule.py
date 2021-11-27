from datetime import datetime


class Schedule:
    def __init__(self, id, schedule_time, duration, active, created_at=datetime.now().replace(microsecond=0),
                 updated_at=datetime.now().replace(microsecond=0)):
        self.id = id
        self.schedule_time = schedule_time
        self.duration = duration
        self.active = active
        self.created_at = created_at
        self.updated_at = updated_at
