import math
import time
from datetime import datetime

from luma.core.render import canvas

from app.display.oleddisplayhelper import OledDisplayHelper
from app.display.oleddisplaypage import OledDisplayPage

FONT_CONSOLAS = 'Consolas.ttf'
FONT_FONTAWESOME = 'fontawesome-webfont.ttf'


class OledDisplay(OledDisplayHelper):
    def __init__(self, config, logger):
        self._set_logger(logger)
        self._set_config(config)

        self.device = self._initialize_display()

    def __show_dashboard(self, display_page):
        font_banner = self._make_font(FONT_CONSOLAS, 12)
        font_icon_1 = self._make_font(FONT_FONTAWESOME, 10)
        font_icon_2 = self._make_font(FONT_FONTAWESOME, 12)
        font_row_1 = self._make_font(FONT_CONSOLAS, 10)
        font_row_2 = self._make_font(FONT_CONSOLAS, 15)
        font_row_3 = self._make_font(FONT_CONSOLAS, 12)
        font_row_4 = self._make_font(FONT_CONSOLAS, 11)

        with canvas(self.device) as draw:
            draw.text((1, 1), text=self.config.get_application_name(), font=font_banner, fill="white")
            draw.text((105, 1), text='\uf012', font=font_icon_1, fill="white")
            draw.text((120, 1), text='\uf043', font=font_icon_2, fill="white")
            draw.line((0, 12, 128, 12), fill="white")

            if display_page == OledDisplayPage.NOW:
                now = datetime.now()
                draw.text((1, 14), text="Now:", font=font_row_1, fill="white")
                self._center_text(draw, 128, 26, text=now.strftime("%H:%M"), font=font_row_2, fill="white")
                self._center_text(draw, 128, 41, text=now.strftime("%d-%m-%Y"), font=font_row_3, fill="white")
                self._center_text(draw, 128, 54, text=now.strftime("(%A)"), font=font_row_4, fill="white")
            elif display_page == OledDisplayPage.NEXT_SCHEDULE:
                draw.text((1, 14), text="Next Schedule:", font=font_row_1, fill="white")
                self._center_text(draw, 128, 26, text="21:30", font=font_row_2, fill="white")
                self._center_text(draw, 128, 41, text="In 2 days", font=font_row_3, fill="white")
                self._center_text(draw, 128, 54, text="4 mins", font=font_row_4, fill="white")
            elif display_page == OledDisplayPage.LAST_RUN:
                draw.text((1, 14), text="Last Run:", font=font_row_1, fill="white")
                self._center_text(draw, 128, 26, text="08:30", font=font_row_2, fill="white")
                self._center_text(draw, 128, 41, text="Yesterday", font=font_row_3, fill="white")
                self._center_text(draw, 128, 54, text="1 hr 1 min 20 secs (A)", font=font_row_4, fill="white")

    def start(self):
        pages = [OledDisplayPage.NOW, OledDisplayPage.NEXT_SCHEDULE, OledDisplayPage.LAST_RUN]
        counter = 0
        change_duration = self.config.get_display_change_duration_sec()

        while True:
            self.__show_dashboard(pages[math.floor(counter / change_duration)])
            counter = counter + 1

            if counter >= 3 * change_duration:
                counter = 0

            time.sleep(1)
