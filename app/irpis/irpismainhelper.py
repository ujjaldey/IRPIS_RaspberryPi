import subprocess
from datetime import datetime, timedelta

# TODO configuration in .env
PING_URL = '1.1.1.1'


class IrpisMainHelper:
    @staticmethod
    def _is_internet_connected():
        command = ['ping', '-c', '1', PING_URL]
        return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

    @staticmethod
    def _calculate_next_schedule_and_duration(schedule_objs):
        now = datetime.now().replace(microsecond=0)
        today_str = now.strftime('%d-%m-%Y')

        schedules = [(datetime.strptime(f'{today_str} {x.schedule_time}', '%d-%m-%Y %H:%M'), x.duration) for x in
                     schedule_objs]

        sorted_schedules = sorted(schedules, key=lambda tup: tup[0])

        sorted_schedules.append((sorted_schedules[0][0] + timedelta(days=1), sorted_schedules[0][1]))

        next_schedule = now

        for counter in range(len(sorted_schedules)):
            if sorted_schedules[counter][0] > now:
                next_schedule = sorted_schedules[counter][0]
                next_duration = sorted_schedules[counter][1]
                break

        return next_schedule, next_duration
