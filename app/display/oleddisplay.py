import math
import time
from datetime import date

from app.util.common import Util
from app.display.oleddisplayenum import OledDisplayEnum
from app.display.oleddisplayhelper import OledDisplayHelper

ESP8266_STATUS_CHECK_TIMEOUT_SEC = 10


class OledDisplay(OledDisplayHelper):
    def __init__(self, logger, config):
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

        self.next_schedule = date.today()
        self.next_duration = 0

        self.last_execution = date.today()
        self.last_duration = 0
        self.last_execution_type = 'Scheduled'

        self.util = Util()

        self.display_off_counter_sec = int(time.time())

    def set_wifi_online(self, online):
        self.wifi_online = online

    def set_esp8266_online(self, online):
        if online:
            self.esp8266_status_check_sec = int(time.time())

        self.esp8266_online = online

    def set_next_schedule(self, next_schedule, duration):
        self.next_schedule = next_schedule
        self.next_duration = duration

    def set_last_execution(self, execution):
        self.last_execution = execution.executed_at
        self.last_duration = execution.duration
        self.last_execution_type = execution.type.capitalize()

    def cleanup(self):
        self._cleanup()

    def start(self):
        pages = [OledDisplayEnum.NOW, OledDisplayEnum.NEXT_SCHEDULE, OledDisplayEnum.LAST_RUN]
        counter = 0
        self.display_off_counter_sec = int(time.time())
        display_change_counter_sec = int(time.time()) - self.config.get_display_change_duration_sec()
        self.esp8266_status_check_sec = int(time.time())

        while True:
            if self.active:
                self._show_dashboard(OledDisplayEnum.ACTIVE)
                counter = 0
                self.display_off_counter_sec = int(time.time())
            else:
                if int(time.time()) >= display_change_counter_sec + self.config.get_display_change_duration_sec():
                    self._show_dashboard(pages[counter])
                    display_change_counter_sec = int(time.time())
                    counter = counter + 1
                    if counter >= len(pages):
                        counter = 0

                if int(time.time()) >= self.display_off_counter_sec + self.config.get_display_timeout_sec():
                    self.display_on_off(False)

            if int(time.time()) >= self.esp8266_status_check_sec + ESP8266_STATUS_CHECK_TIMEOUT_SEC:
                self.esp8266_online = False
                self.esp8266_status_check_sec = int(time.time())

            time.sleep(.5)
