import subprocess
from time import sleep

# TODO configuration in .env
PING_URL = '1.1.1.1'


class IrpisMainHelper:
    def _set_logger(self, logger):
        self.logger = logger

    def _set_config(self, config):
        self.config = config

    def _set_display(self, display):
        self.display = display

    @staticmethod
    def __is_internet_connected():
        command = ['ping', '-c', '1', PING_URL]
        return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

    def _main(self):
        on = True
        while True:
            self.logger.info("Calling IRPIS main")
            # TODO should be checked at certain interval only
            self.display.set_wifi_online(self.__is_internet_connected())

            # self.display.enable_backlight(on)
            # sleep(5 if on else 30)
            # on = not on

            sleep(1)
