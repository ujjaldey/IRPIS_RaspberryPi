from datetime import datetime


class NextSchedule:
    def __init__(self, next_schedule_at, duration, created_at=datetime.now().replace(microsecond=0),
                 updated_at=datetime.now().replace(microsecond=0)):
        self.next_schedule_at = next_schedule_at
        self.duration = duration
        self.created_at = created_at
        self.updated_at = updated_at
