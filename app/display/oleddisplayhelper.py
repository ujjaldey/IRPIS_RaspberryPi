from time import time
from datetime import datetime
from pathlib import Path

from PIL import ImageFont
from luma.core import cmdline, error
from luma.core.render import canvas

from app.enum.irpisenum import IrpisEnum
from app.enum.oleddisplayenum import OledDisplayEnum


class OledDisplayHelper:
    def _set_active(self, active, duration=0):
        self.active = active
        self.duration = duration
        self.active_end_sec = int(time()) + self.duration

    def _set_display_off_counter_sec(self, display_off_counter_sec):
        self.display_off_counter_sec = display_off_counter_sec

    # def __do_nothing(self, obj):
    #     pass

    def _initialize_display(self):
        actual_args = ['--interface', 'spi', '--display', 'ssd1309', '--mode', '1']
        parser = cmdline.create_parser(IrpisEnum.APPLICATION_NAME.value)
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
    def _center_text(draw, width, y_value, text, fill=OledDisplayEnum.FONT_FILL_COLOR.value, font=None):
        x_value = (width - draw.textsize(text, font=font)[0]) / 2
        draw.text((x_value, y_value), text=text, font=font, fill=fill)

    @staticmethod
    def __show_wifi_status(draw):
        draw.line((103, 3, 114, 10), fill=OledDisplayEnum.FONT_FILL_COLOR.value)

    @staticmethod
    def __show_esp8266_status(draw):
        draw.line((116, 3, 127, 10), fill=OledDisplayEnum.FONT_FILL_COLOR.value)

    def _show_dashboard(self, display_page):
        font_banner = self._make_font(OledDisplayEnum.FONT_CONSOLAS.value, OledDisplayEnum.FONT_SIZE_BANNER.value)
        font_header = self._make_font(OledDisplayEnum.FONT_CONSOLAS.value, OledDisplayEnum.FONT_SIZE_HEADER.value)
        font_icon_1 = self._make_font(OledDisplayEnum.FONT_FONTAWESOME.value, OledDisplayEnum.FONT_SIZE_ICON_1.value)
        font_icon_2 = self._make_font(OledDisplayEnum.FONT_FONTAWESOME.value, OledDisplayEnum.FONT_SIZE_ICON_2.value)
        font_row_1 = self._make_font(OledDisplayEnum.FONT_CONSOLAS.value, OledDisplayEnum.FONT_SIZE_ROW_1.value)
        font_row_2 = self._make_font(OledDisplayEnum.FONT_CONSOLAS.value, OledDisplayEnum.FONT_SIZE_ROW_2.value)
        font_row_3 = self._make_font(OledDisplayEnum.FONT_CONSOLAS.value, OledDisplayEnum.FONT_SIZE_ROW_3.value)
        font_row_4 = self._make_font(OledDisplayEnum.FONT_CONSOLAS.value, OledDisplayEnum.FONT_SIZE_ROW_4.value)
        font_row_5 = self._make_font(OledDisplayEnum.FONT_CONSOLAS.value, OledDisplayEnum.FONT_SIZE_ROW_5.value)

        try:
            with canvas(self.device) as draw:
                if not display_page == OledDisplayEnum.DISPLAY_PAGE_BANNER:
                    draw.text((1, 1), text=IrpisEnum.APPLICATION_NAME.value, font=font_header,
                              fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                    draw.text((103, 1), text='\uf012', font=font_icon_1, fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                    draw.text((119, 1), text='\uf043', font=font_icon_2, fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                    draw.line((0, 12, 128, 12), fill=OledDisplayEnum.FONT_FILL_COLOR.value)

                    if not self.wifi_online:
                        self.__show_wifi_status(draw)

                    if not self.esp8266_online:
                        self.__show_esp8266_status(draw)

                    elif display_page == OledDisplayEnum.DISPLAY_PAGE_ACTIVE:
                        draw.text((1, 14), text='Active:', font=font_row_1, fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                        self._center_text(draw, 128, 26,
                                          text=self.common.convert_secs_to_human_format(
                                              self.active_end_sec - int(time()), True),
                                          font=font_row_2, fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                        self._center_text(draw, 128, 41, text='remaining', font=font_row_3,
                                          fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                        self._center_text(draw, 128, 53, text='(watering)', font=font_row_4,
                                          fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                    elif display_page == OledDisplayEnum.DISPLAY_PAGE_NOW:
                        now = datetime.now().replace(microsecond=0)
                        draw.text((1, 14), text='Now:', font=font_row_1, fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                        self._center_text(draw, 128, 26, text=now.strftime('%H:%M'), font=font_row_2,
                                          fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                        self._center_text(draw, 128, 41, text=now.strftime('%d-%m-%Y'), font=font_row_3,
                                          fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                        self._center_text(draw, 128, 53, text=now.strftime('(%A)'), font=font_row_4,
                                          fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                    elif display_page == OledDisplayEnum.DISPLAY_PAGE_NEXT_SCHEDULE:
                        draw.text((1, 14), text='Next Schedule:', font=font_row_1,
                                  fill=OledDisplayEnum.FONT_FILL_COLOR.value)

                        if self.next_schedule:
                            self._center_text(draw, 128, 26, text=self.next_schedule.strftime('%H:%M'), font=font_row_2,
                                              fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                            self._center_text(draw, 128, 41,
                                              text=self.common.convert_date_to_human_format(self.next_schedule),
                                              font=font_row_3, fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                            self._center_text(draw, 128, 53,
                                              text=self.common.convert_secs_to_human_format(self.next_duration, True),
                                              font=font_row_4, fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                        else:
                            self._center_text(draw, 128, 26, text='No', font=font_row_2,
                                              fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                            self._center_text(draw, 128, 41,
                                              text='Next',
                                              font=font_row_3, fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                            self._center_text(draw, 128, 53,
                                              text='Schedule',
                                              font=font_row_4, fill=OledDisplayEnum.FONT_FILL_COLOR.value)

                    elif display_page == OledDisplayEnum.DISPLAY_PAGE_LAST_RUN:
                        execution_type_str = f' ({self.last_execution_type})' if self.last_execution_type else ''
                        draw.text((1, 14), text=f'Last Run{execution_type_str}:', font=font_row_1,
                                  fill=OledDisplayEnum.FONT_FILL_COLOR.value)

                        if self.last_execution_type:
                            self._center_text(draw, 128, 26, text=self.last_execution.strftime('%H:%M'),
                                              font=font_row_2,
                                              fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                            self._center_text(draw, 128, 41,
                                              text=self.common.convert_date_to_human_format(self.last_execution),
                                              font=font_row_3, fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                            self._center_text(draw, 128, 53,
                                              text=f'{self.common.convert_secs_to_human_format(self.last_duration, True)} ',
                                              font=font_row_4, fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                        else:
                            self._center_text(draw, 128, 26, text='No', font=font_row_2,
                                              fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                            self._center_text(draw, 128, 41,
                                              text='Previous',
                                              font=font_row_3, fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                            self._center_text(draw, 128, 53,
                                              text='Executions',
                                              font=font_row_4, fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                else:
                    self._center_text(draw, 128, 2, text=IrpisEnum.APPLICATION_NAME.value, font=font_banner,
                                      fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                    draw.line((30, 24, 98, 24), fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                    self._center_text(draw, 128, 27, text='IOT Remote', font=font_row_5,
                                      fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                    self._center_text(draw, 128, 37, text='Plant Irrigation System', font=font_row_5,
                                      fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                    draw.line((5, 48, 123, 48), fill=OledDisplayEnum.FONT_FILL_COLOR.value)
                    self._center_text(draw, 128, 53, text=self.common.greet_time(), font=font_row_3,
                                      fill=OledDisplayEnum.FONT_FILL_COLOR.value)
        except Exception as ex:
            print(ex)

    def display_on_off(self, on_off):
        if on_off:
            self._set_display_off_counter_sec(int(time()))
            self.device.show()
        else:
            self.device.hide()

    def set_active(self, active, duration=0):
        self._set_active(active, duration)
