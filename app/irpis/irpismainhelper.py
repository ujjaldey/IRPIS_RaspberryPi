import subprocess

# TODO configuration in .env
PING_URL = '1.1.1.1'


class IrpisMainHelper:
    @staticmethod
    def _is_internet_connected():
        command = ['ping', '-c', '1', PING_URL]
        return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0
