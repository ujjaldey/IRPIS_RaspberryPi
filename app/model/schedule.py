from datetime import datetime


class Schedule:
    def __init__(self, next_schedule, duration, created_at=datetime.now().replace(microsecond=0),
                 updated_at=datetime.now().replace(microsecond=0)):
        self.next_schedule = next_schedule
        self.duration = duration
        self.created_at = created_at
        self.updated_at = updated_at
