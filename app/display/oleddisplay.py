import math
import time

from app.util.common import Util
from app.display.oleddisplayenum import OledDisplayEnum
from app.display.oleddisplayhelper import OledDisplayHelper

ESP8266_STATUS_CHECK_TIMEOUT_SEC = 10


class OledDisplay(OledDisplayHelper):
    def __init__(self, config, logger):
        self.logger = logger
        self.config = config

        self.wifi_online = False
        self.esp8266_online = False

        self._set_active(False)
        self.esp8266_status_check_sec = int(time.time())

        self.device = self._initialize_display()
        self.active = False
        self.wifi_online = False
        self.esp8266_online = False
        self.duration = 0
        self.active_end_sec = 0

        self.util = Util()

    def set_wifi_online(self, online):
        self.wifi_online = online

    def set_esp8266_online(self, online):
        if online:
            self.esp8266_status_check_sec = int(time.time())

        self.esp8266_online = online

    def cleanup(self):
        self._cleanup()

    def start(self):
        pages = [OledDisplayEnum.NOW, OledDisplayEnum.NEXT_SCHEDULE, OledDisplayEnum.LAST_RUN]
        counter = 0
        display_off_counter_sec = int(time.time())
        self.esp8266_status_check_sec = int(time.time())
        change_duration = self.config.get_display_change_duration_sec()
        backlight_enabled = True

        while True:
            if self.active:
                self.duration = self.duration - .5
                self._show_dashboard(OledDisplayEnum.ACTIVE)
                counter = 0
                display_off_counter_sec = int(time.time())
                backlight_enabled = True
            else:
                self._show_dashboard(pages[math.floor(counter / change_duration)])
                counter = counter + 1

                if counter >= 3 * change_duration:
                    counter = 0

                if backlight_enabled and int(
                        time.time()) >= display_off_counter_sec + self.config.get_display_timeout_sec():
                    backlight_enabled = False
                    self.enable_backlight(backlight_enabled)

            if int(time.time()) >= self.esp8266_status_check_sec + ESP8266_STATUS_CHECK_TIMEOUT_SEC:
                self.esp8266_online = False
                self.esp8266_status_check_sec = int(time.time())

            time.sleep(.5)
