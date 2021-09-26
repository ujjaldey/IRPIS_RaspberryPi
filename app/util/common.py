import os
from datetime import date, datetime, timedelta

from app.dao.schedule_dao import ScheduleDao


class Common:
    @staticmethod
    def convert_secs_to_human_format(seconds, short=False):
        input_seconds = seconds
        day_str = 'day' if seconds < 3600 else 'd'
        hr_str = 'hour' if not short else 'hr' if seconds < 3600 else 'h'
        min_str = 'minute' if not short else 'min' if seconds < 3600 else 'm'
        sec_str = 'second' if not short else 'sec' if seconds < 3600 else 's'
        duration_units = (
            (day_str, 60 * 60 * 24),
            (hr_str, 60 * 60),
            (min_str, 60),
            (sec_str, 1)
        )

        if seconds == 0:
            return '0 ' + ('second' if not short else 'sec')

        parts = []
        for unit, div in duration_units:
            amount, seconds = divmod(int(seconds), div)
            if amount > 0:
                parts.append('{} {}{}'.format(
                    amount, unit, '' if (amount == 1 or (short and input_seconds >= 3600)) else 's'))
        return ' '.join(parts)

    @staticmethod
    def convert_date_to_human_format(date_time):
        diff = (date_time.date() - date.today()).days

        if diff == 0:
            human_date = "Today"
        elif diff == -1:
            human_date = "Yesterday"
        elif diff == 1:
            human_date = "Tomorrow"
        elif diff == 2:
            human_date = "Day after Tomorrow"
        elif abs(diff) < 4:
            human_date = f"{abs(diff)} days ago" if diff < 0 else f"In {abs(diff)} days"
        elif abs(diff) <= 7:
            last_next = "Last" if diff < 0 else "Next" if diff == 7 else "This"
            day = date_time.strftime("%A")
            human_date = f"{last_next} {day}"
        else:
            day = date_time.strftime("%d-%m-%Y")
            human_date = f"On {day}"

        return human_date

    @staticmethod
    def calculate_next_schedule_and_duration(conn, curr_schedule):
        schedule_dao = ScheduleDao()
        schedule_objs = schedule_dao.select(conn)
        today_str = curr_schedule.strftime('%d-%m-%Y')

        schedules = [(datetime.strptime(f'{today_str} {x.schedule_time}', '%d-%m-%Y %H:%M'), x.duration) for x in
                     schedule_objs]

        sorted_schedules = sorted(schedules, key=lambda tup: tup[0])

        if len(sorted_schedules) > 0:
            sorted_schedules.append((sorted_schedules[0][0] + timedelta(days=1), sorted_schedules[0][1]))

            next_schedule = curr_schedule

            for counter in range(len(sorted_schedules)):
                if sorted_schedules[counter][0] > curr_schedule:
                    next_schedule = sorted_schedules[counter][0]
                    next_duration = sorted_schedules[counter][1]
                    break
        else:
            next_schedule = datetime.now().replace(microsecond=0) + timedelta(days=1)
            # TODO the default duration if not schedule to be parameterized
            next_duration = 60

        return next_schedule, next_duration

    @staticmethod
    def reboot():
        os.system('sudo reboot')

    @staticmethod
    def shutdown():
        os.system('sudo shutdown now')
