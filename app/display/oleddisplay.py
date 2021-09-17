import math
import time
from datetime import datetime

from luma.core.render import canvas

from app.display.oleddisplayhelper import OledDisplayHelper
from app.display.oleddisplayenum import OledDisplayEnum

FONT_CONSOLAS = 'Consolas.ttf'
FONT_FONTAWESOME = 'fontawesome-webfont.ttf'
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

    def set_wifi_online(self, online):
        self.wifi_online = online

    def set_esp8266_online(self, online):
        if online:
            self.esp8266_status_check_sec = int(time.time())

        self.esp8266_online = online

    def cleanup(self):
        self._cleanup()

    @staticmethod
    def __show_wifi_status(draw):
        draw.line((103, 3, 114, 10), fill="white")

    @staticmethod
    def __show_esp8266_status(draw):
        draw.line((116, 3, 127, 10), fill="white")

    def __show_dashboard(self, display_page):
        font_banner = self._make_font(FONT_CONSOLAS, 12)
        font_icon_1 = self._make_font(FONT_FONTAWESOME, 10)
        font_icon_2 = self._make_font(FONT_FONTAWESOME, 12)
        font_row_1 = self._make_font(FONT_CONSOLAS, 10)
        font_row_2 = self._make_font(FONT_CONSOLAS, 15)
        font_row_3 = self._make_font(FONT_CONSOLAS, 12)
        font_row_4 = self._make_font(FONT_CONSOLAS, 10)

        with canvas(self.device) as draw:
            draw.text((1, 1), text=self.config.get_application_name(), font=font_banner, fill="white")
            draw.text((103, 1), text='\uf012', font=font_icon_1, fill="white")
            draw.text((119, 1), text='\uf043', font=font_icon_2, fill="white")
            draw.line((0, 12, 128, 12), fill="white")

            if not self.wifi_online:
                self.__show_wifi_status(draw)

            if not self.esp8266_online:
                self.__show_esp8266_status(draw)

            if display_page == OledDisplayEnum.ACTIVE:
                draw.text((1, 14), text="Active:", font=font_row_1, fill="white")
                self._center_text(draw, 128, 26, text=str(self.active_end_sec - int(time.time())) + " sec",
                                  font=font_row_2, fill="white")
                self._center_text(draw, 128, 41, text="remaining", font=font_row_3,
                                  fill="white")
                self._center_text(draw, 128, 53, text="(watering)", font=font_row_4, fill="white")
            elif display_page == OledDisplayEnum.NOW:
                now = datetime.now()
                draw.text((1, 14), text="Now:", font=font_row_1, fill="white")
                self._center_text(draw, 128, 26, text=now.strftime("%H:%M"), font=font_row_2, fill="white")
                self._center_text(draw, 128, 41, text=now.strftime("%d-%m-%Y"), font=font_row_3, fill="white")
                self._center_text(draw, 128, 53, text=now.strftime("(%A)"), font=font_row_4, fill="white")
            elif display_page == OledDisplayEnum.NEXT_SCHEDULE:
                draw.text((1, 14), text="Next Schedule:", font=font_row_1, fill="white")
                self._center_text(draw, 128, 26, text="21:30", font=font_row_2, fill="white")
                self._center_text(draw, 128, 41, text="In 2 days", font=font_row_3, fill="white")
                self._center_text(draw, 128, 53, text="4 mins", font=font_row_4, fill="white")
            elif display_page == OledDisplayEnum.LAST_RUN:
                draw.text((1, 14), text="Last Run:", font=font_row_1, fill="white")
                self._center_text(draw, 128, 26, text="08:30", font=font_row_2, fill="white")
                self._center_text(draw, 128, 41, text="Yesterday", font=font_row_3, fill="white")
                self._center_text(draw, 128, 53, text="1 hr 1 min 20 secs (A)", font=font_row_4, fill="white")

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
                self.__show_dashboard(OledDisplayEnum.ACTIVE)
                counter = 0
                display_off_counter_sec = int(time.time())
                backlight_enabled = True
            else:
                self.__show_dashboard(pages[math.floor(counter / change_duration)])
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
