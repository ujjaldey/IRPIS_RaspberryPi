class Util:
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
                parts.append('{} {}{}'.format(amount, unit, '' if (amount == 1 or input_seconds >= 3600) else 's'))
        return ' '.join(parts)
