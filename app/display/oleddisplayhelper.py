import time
from datetime import datetime
from pathlib import Path

from PIL import ImageFont
from luma.core import cmdline, error
from luma.core.render import canvas

from app.display.oleddisplayenum import OledDisplayEnum

FONT_CONSOLAS = 'Consolas.ttf'
FONT_FONTAWESOME = 'fontawesome-webfont.ttf'


class OledDisplayHelper:
    def _set_active(self, active, duration=0):
        self.active = active
        self.duration = duration
        self.active_end_sec = int(time.time()) + self.duration

    # def __do_nothing(self, obj):
    #     pass

    def _initialize_display(self):
        actual_args = ['--interface', 'spi', '--display', 'ssd1309', '--mode', '1']
        parser = cmdline.create_parser(self.config.get_application_name())
        args = parser.parse_args(actual_args)

        try:
            device = cmdline.create_device(args)
            # device.cleanup = __do_nothing
            return device
        except error.Error as e:
            self.logger.error('Error in initializing display: ' + str(e))
            return None

    def _cleanup(self):
        self.device.cleanup()

    @staticmethod
    def _make_font(name, size):
        font_path = str(Path(__file__).resolve().parent.parent.parent.joinpath('resources', 'fonts', name))
        return ImageFont.truetype(font_path, size)

    @staticmethod
    def _center_text(draw, width, y_value, text, fill='white', font=None):
        x_value = (width - draw.textsize(text, font=font)[0]) / 2
        draw.text((x_value, y_value), text=text, font=font, fill=fill)

    @staticmethod
    def __show_wifi_status(draw):
        draw.line((103, 3, 114, 10), fill='white')

    @staticmethod
    def __show_esp8266_status(draw):
        draw.line((116, 3, 127, 10), fill='white')

    def _show_dashboard(self, display_page):
        font_banner = self._make_font(FONT_CONSOLAS, 12)
        font_icon_1 = self._make_font(FONT_FONTAWESOME, 10)
        font_icon_2 = self._make_font(FONT_FONTAWESOME, 12)
        font_row_1 = self._make_font(FONT_CONSOLAS, 10)
        font_row_2 = self._make_font(FONT_CONSOLAS, 15)
        font_row_3 = self._make_font(FONT_CONSOLAS, 12)
        font_row_4 = self._make_font(FONT_CONSOLAS, 10)

        try:
            with canvas(self.device) as draw:
                draw.text((1, 1), text=self.config.get_application_name(), font=font_banner, fill='white')
                draw.text((103, 1), text='\uf012', font=font_icon_1, fill='white')
                draw.text((119, 1), text='\uf043', font=font_icon_2, fill='white')
                draw.line((0, 12, 128, 12), fill='white')

                if not self.wifi_online:
                    self.__show_wifi_status(draw)

                if not self.esp8266_online:
                    self.__show_esp8266_status(draw)

                if display_page == OledDisplayEnum.ACTIVE:
                    draw.text((1, 14), text='Active:', font=font_row_1, fill='white')
                    self._center_text(draw, 128, 26,
                                      text=self.util.convert_secs_to_human_format(
                                          self.active_end_sec - int(time.time()), True),
                                      font=font_row_2, fill='white')
                    self._center_text(draw, 128, 41, text='remaining', font=font_row_3,
                                      fill='white')
                    self._center_text(draw, 128, 53, text='(watering)', font=font_row_4, fill='white')
                elif display_page == OledDisplayEnum.NOW:
                    now = datetime.now()
                    draw.text((1, 14), text='Now:', font=font_row_1, fill='white')
                    self._center_text(draw, 128, 26, text=now.strftime('%H:%M'), font=font_row_2, fill='white')
                    self._center_text(draw, 128, 41, text=now.strftime('%d-%m-%Y'), font=font_row_3, fill='white')
                    self._center_text(draw, 128, 53, text=now.strftime('(%A)'), font=font_row_4, fill='white')
                elif display_page == OledDisplayEnum.NEXT_SCHEDULE:
                    draw.text((1, 14), text='Next Schedule:', font=font_row_1, fill='white')
                    self._center_text(draw, 128, 26, text=self.next_schedule.strftime('%H:%M'), font=font_row_2,
                                      fill='white')
                    self._center_text(draw, 128, 41, text=self.util.convert_date_to_human_format(self.next_schedule),
                                      font=font_row_3, fill='white')
                    self._center_text(draw, 128, 53,
                                      text=self.util.convert_secs_to_human_format(self.next_duration, True),
                                      font=font_row_4, fill='white')
                elif display_page == OledDisplayEnum.LAST_RUN:
                    draw.text((1, 14), text='Last Run:', font=font_row_1, fill='white')
                    self._center_text(draw, 128, 26, text=self.last_execution.strftime('%H:%M'), font=font_row_2,
                                      fill='white')
                    self._center_text(draw, 128, 41, text=self.util.convert_date_to_human_format(self.last_execution),
                                      font=font_row_3, fill='white')
                    self._center_text(draw, 128, 53,
                                      text=f'{self.util.convert_secs_to_human_format(self.last_duration, True)} ' +
                                           f'({self.last_execution_type})',
                                      font=font_row_4, fill='white')
        except Exception as e:
            print(e)

    def enable_backlight(self, on_off):
        if on_off:
            self.device.show()
        else:
            self.device.hide()

    def set_active(self, active, duration=0):
        self._set_active(active, duration)
