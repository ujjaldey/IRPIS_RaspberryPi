from time import time, sleep
from datetime import date

from app.display.oleddisplayhelper import OledDisplayHelper
from app.enum.oleddisplayenum import OledDisplayEnum
from app.util.common import Common


class OledDisplay(OledDisplayHelper):
    def __init__(self, logger, config):
        self.logger = logger
        self.config = config

        self.wifi_online = False
        self.esp8266_online = False

        self._set_active(False)
        self.esp8266_status_check_sec = int(time())

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

        self.common = Common()

        self.display_off_counter_sec = int(time())

    def set_wifi_online(self, online):
        self.wifi_online = online

    def set_esp8266_online(self, online):
        if online:
            self.esp8266_status_check_sec = int(time())

        self.esp8266_online = online

    def set_next_schedule(self, schedule):
        self.next_schedule = schedule.next_schedule_at
        self.next_duration = schedule.duration

    def set_last_execution(self, execution):
        self.last_execution = execution.executed_at
        self.last_duration = execution.duration
        self.last_execution_type = execution.type.capitalize()

    def cleanup(self):
        self._cleanup()

    def start(self):
        pages = [OledDisplayEnum.DISPLAY_PAGE_NOW,
                 OledDisplayEnum.DISPLAY_PAGE_NEXT_SCHEDULE,
                 OledDisplayEnum.DISPLAY_PAGE_LAST_RUN]
        counter = 0
        self.display_off_counter_sec = int(time())
        display_change_counter_sec = int(time()) - self.config.get_display_change_duration_sec()
        self.esp8266_status_check_sec = int(time())

        self._show_dashboard(OledDisplayEnum.DISPLAY_PAGE_BANNER)
        sleep(5)

        while True:
            if self.active:
                self._show_dashboard(OledDisplayEnum.DISPLAY_PAGE_ACTIVE)
                counter = 0
                self.display_off_counter_sec = int(time())
            else:
                if int(time()) >= display_change_counter_sec + self.config.get_display_change_duration_sec():
                    self._show_dashboard(pages[counter])
                    display_change_counter_sec = int(time())
                    counter = counter + 1
                    if counter >= len(pages):
                        counter = 0

                display_timeout = self.config.get_display_timeout_sec()
                if display_timeout >= 0 and int(time()) >= self.display_off_counter_sec + display_timeout:
                    self.display_on_off(False)

            if int(time()) >= \
                    self.esp8266_status_check_sec + OledDisplayEnum.ESP8266_STATUS_CHECK_TIMEOUT_SEC.value:
                self.esp8266_online = False
                self.esp8266_status_check_sec = int(time())

            sleep(.5)
