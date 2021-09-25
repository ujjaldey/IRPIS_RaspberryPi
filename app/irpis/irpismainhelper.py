import subprocess

# TODO configuration in .env

PING_URL = '1.1.1.1'


class IrpisMainHelper:
    @staticmethod
    def _is_internet_connected():
        command = ['ping', '-c', '1', PING_URL]
        return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

    def _calculate_next_schedule_and_duration(self, conn, now):
        return self.common.calculate_next_schedule_and_duration(conn, now)
