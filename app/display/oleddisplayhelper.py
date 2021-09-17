import time
from pathlib import Path

from PIL import ImageFont
from luma.core import cmdline, error


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
    def _center_text(draw, width, y_value, text, fill="white", font=None):
        x_value = (width - draw.textsize(text, font=font)[0]) / 2
        draw.text((x_value, y_value), text=text, font=font, fill=fill)

    def enable_backlight(self, on_off):
        if on_off:
            self.device.show()
        else:
            self.device.hide()

    def set_active(self, active, duration=0):
        self._set_active(active, duration)
